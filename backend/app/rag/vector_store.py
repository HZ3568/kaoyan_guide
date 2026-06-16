import json
import struct
from dataclasses import dataclass
from typing import Any

import redis
from redis.exceptions import ResponseError

from app.core.config import settings
from app.core.redis import get_redis

DIMENSION_REBUILD_NOTICE = (
    "如果 EMBEDDING_DIMENSION 发生变化，需要删除旧 Redis Vector Index 并重新向量化文档，"
    "否则旧索引维度可能与新 embedding 不一致。"
)

try:
    from redis.commands.search.field import NumericField, TagField, TextField, VectorField
    from redis.commands.search.query import Query
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("redis-py RediSearch support is required for Redis Vector") from exc

try:
    from redis.commands.search.index_definition import IndexDefinition, IndexType
except ImportError:  # pragma: no cover
    from redis.commands.search.indexDefinition import IndexDefinition, IndexType


class VectorStoreError(RuntimeError):
    pass


@dataclass
class RedisVectorHit:
    chunk_id: int
    document_id: int
    score: float
    distance: float
    redis_key: str


class RedisVectorStore:
    def __init__(
        self,
        redis_client: redis.Redis | None = None,
        *,
        index_name: str | None = None,
        key_prefix: str | None = None,
        dim: int | None = None,
        distance_metric: str | None = None,
    ) -> None:
        self.redis = redis_client or get_redis()
        self.index_name = index_name or settings.REDIS_VECTOR_INDEX_NAME
        self.key_prefix = (key_prefix or settings.REDIS_VECTOR_KEY_PREFIX).rstrip(":")
        self.dim = dim or settings.embedding_dimension
        self.distance_metric = (distance_metric or settings.REDIS_VECTOR_DISTANCE_METRIC).upper()

    def key_for_chunk(self, chunk_id: int) -> str:
        return f"{self.key_prefix}:{chunk_id}"

    def ensure_index(self) -> None:
        try:
            raw_info = self.redis.ft(self.index_name).info()
            existing_dim = self._extract_vector_dimension(raw_info)
            if existing_dim is not None and existing_dim != self.dim:
                raise VectorStoreError(
                    "Redis Vector index dimension mismatch: "
                    f"index={self.index_name}, existing_dim={existing_dim}, "
                    f"configured_dim={self.dim}. {DIMENSION_REBUILD_NOTICE}"
                )
            return
        except ResponseError as exc:
            message = str(exc).lower()
            if "unknown index name" not in message and "no such index" not in message:
                raise VectorStoreError(f"Redis Vector index check failed: {exc}") from exc

        schema = (
            NumericField("chunk_id"),
            NumericField("document_id"),
            NumericField("user_id"),
            NumericField("goal_id"),
            NumericField("knowledge_base_id"),
            TagField("domain"),
            TagField("category"),
            TextField("content_preview"),
            TextField("metadata"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.dim,
                    "DISTANCE_METRIC": self.distance_metric,
                    "INITIAL_CAP": 1000,
                    "M": 16,
                    "EF_CONSTRUCTION": 200,
                },
            ),
        )
        definition = IndexDefinition(prefix=[f"{self.key_prefix}:"], index_type=IndexType.HASH)
        try:
            self.redis.ft(self.index_name).create_index(schema, definition=definition)
        except ResponseError as exc:
            message = str(exc).lower()
            if "index already exists" not in message:
                raise VectorStoreError(f"Redis Vector index creation failed: {exc}") from exc

    def drop_index(self, *, delete_documents: bool = False) -> None:
        try:
            self.redis.ft(self.index_name).dropindex(delete_documents=delete_documents)
        except ResponseError as exc:
            message = str(exc).lower()
            if "unknown index name" not in message and "no such index" not in message:
                raise VectorStoreError(f"Redis Vector index drop failed: {exc}") from exc

    def index_info(self) -> dict[str, Any]:
        try:
            raw_info = self.redis.ft(self.index_name).info()
        except ResponseError as exc:
            message = str(exc).lower()
            if "unknown index name" in message or "no such index" in message:
                return {
                    "exists": False,
                    "index_name": self.index_name,
                    "key_prefix": self.key_prefix,
                    "embedding_dim": self.dim,
                    "distance_metric": self.distance_metric,
                }
            raise VectorStoreError(f"Redis Vector index info failed: {exc}") from exc

        actual_dim = self._extract_vector_dimension(raw_info)
        info = {self._to_text(key): self._to_text(value) for key, value in raw_info.items()}
        return {
            "exists": True,
            "index_name": self.index_name,
            "key_prefix": self.key_prefix,
            "embedding_dim": actual_dim or self.dim,
            "configured_embedding_dim": self.dim,
            "dimension_mismatch": actual_dim is not None and actual_dim != self.dim,
            "dimension_notice": DIMENSION_REBUILD_NOTICE,
            "distance_metric": self.distance_metric,
            "num_docs": int(float(info.get("num_docs", 0))),
            "indexing": info.get("indexing"),
            "hash_indexing_failures": int(float(info.get("hash_indexing_failures", 0))),
        }

    def upsert_chunk(
        self,
        *,
        chunk_id: int,
        document_id: int,
        user_id: int,
        goal_id: int | None,
        knowledge_base_id: int | None,
        domain: str | None,
        category: str | None,
        embedding: list[float],
        content_preview: str,
        metadata: dict[str, Any],
    ) -> str:
        self._validate_embedding(embedding)
        key = self.key_for_chunk(chunk_id)
        mapping: dict[str, Any] = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "user_id": user_id,
            "goal_id": goal_id or 0,
            "knowledge_base_id": knowledge_base_id or 0,
            "domain": domain or "",
            "category": category or "",
            "content_preview": content_preview[:500],
            "metadata": json.dumps(metadata, ensure_ascii=False, default=str),
            "embedding": self.embedding_to_bytes(embedding),
        }
        try:
            self.redis.hset(key, mapping=mapping)
        except redis.RedisError as exc:
            raise VectorStoreError(f"Redis Vector chunk write failed: {exc}") from exc
        return key

    def search(
        self,
        *,
        embedding: list[float],
        top_k: int,
        user_id: int,
        filters: dict[str, Any] | None = None,
    ) -> list[RedisVectorHit]:
        self._validate_embedding(embedding)
        self.ensure_index()
        safe_top_k = max(1, min(int(top_k), 100))
        query_string = self._build_query(safe_top_k, user_id=user_id, filters=filters or {})
        query = (
            Query(query_string)
            .return_fields("chunk_id", "document_id", "score")
            .sort_by("score")
            .paging(0, safe_top_k)
            .dialect(2)
        )
        try:
            result = self.redis.ft(self.index_name).search(
                query,
                query_params={"vec": self.embedding_to_bytes(embedding)},
            )
        except ResponseError as exc:
            raise VectorStoreError(f"Redis Vector search failed: {exc}") from exc

        hits: list[RedisVectorHit] = []
        for doc in result.docs:
            distance = float(self._get_doc_value(doc, "score") or 0.0)
            hits.append(
                RedisVectorHit(
                    chunk_id=int(float(self._get_doc_value(doc, "chunk_id") or 0)),
                    document_id=int(float(self._get_doc_value(doc, "document_id") or 0)),
                    score=self._distance_to_score(distance),
                    distance=distance,
                    redis_key=self._to_text(doc.id),
                )
            )
        return [hit for hit in hits if hit.chunk_id > 0]

    def _build_query(self, top_k: int, *, user_id: int, filters: dict[str, Any]) -> str:
        clauses = [f"@user_id:[{int(user_id)} {int(user_id)}]"]
        for field in ("goal_id", "knowledge_base_id"):
            value = filters.get(field)
            if value:
                clauses.append(f"@{field}:[{int(value)} {int(value)}]")
        for field in ("domain", "category"):
            value = filters.get(field)
            if value:
                clauses.append(f"@{field}:{{{self._escape_tag(value)}}}")
        filter_expr = " ".join(clauses)
        return f"({filter_expr})=>[KNN {top_k} @embedding $vec AS score]"

    def _distance_to_score(self, distance: float) -> float:
        if self.distance_metric == "COSINE":
            return 1.0 - distance
        return -distance

    def _validate_embedding(self, embedding: list[float]) -> None:
        if len(embedding) != self.dim:
            raise VectorStoreError(
                f"Embedding dimension mismatch: Redis index expects {self.dim}, got {len(embedding)}"
            )

    @staticmethod
    def embedding_to_bytes(embedding: list[float]) -> bytes:
        return struct.pack(f"{len(embedding)}f", *embedding)

    @staticmethod
    def _escape_tag(value: Any) -> str:
        special_chars = set(r',.<>{}[]"' + r"':;!@#$%^&*()-+=~| ")
        text = str(value)
        return "".join(f"\\{char}" if char in special_chars else char for char in text)

    @staticmethod
    def _to_text(value: Any) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)

    @classmethod
    def _get_doc_value(cls, doc: Any, field: str) -> str | None:
        value = getattr(doc, field, None)
        if value is None:
            return None
        return cls._to_text(value)

    @classmethod
    def _extract_vector_dimension(cls, raw_info: dict[str, Any]) -> int | None:
        attributes = raw_info.get("attributes") or raw_info.get(b"attributes")
        if attributes is None:
            return None
        flat_values = cls._flatten(attributes)
        for index, value in enumerate(flat_values):
            if cls._to_text(value).upper() == "DIM" and index + 1 < len(flat_values):
                try:
                    return int(float(cls._to_text(flat_values[index + 1])))
                except ValueError:
                    return None
        return None

    @classmethod
    def _flatten(cls, value: Any) -> list[Any]:
        if isinstance(value, (list, tuple)):
            items: list[Any] = []
            for item in value:
                items.extend(cls._flatten(item))
            return items
        return [value]
