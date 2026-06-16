import json
import re
from typing import Any

from app.llm.client import LLMClient, LLMError, LLMMessage, get_llm_client


class AiTaskAssistant:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or get_llm_client()
        self.last_error: str | None = None

    def optimize_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        fallback = self._fallback_optimize(payload)
        self.last_error = None
        try:
            response = self.llm_client.generate(
                [
                    LLMMessage(
                        role="system",
                        content=(
                            "你是学习任务表达优化助手。只优化用户已有任务，不改变用户学习目标。"
                            "必须输出 JSON。"
                        ),
                    ),
                    LLMMessage(
                        role="user",
                        content=(
                            "请把下面任务优化成更具体、可执行、可反馈的学习任务。"
                            "输出 JSON，字段为 suggested_content、suggested_category、"
                            "suggested_estimated_minutes、suggested_priority、reason、warnings。\n"
                            f"输入：{json.dumps(payload, ensure_ascii=False, default=str)}"
                        ),
                    ),
                ]
            )
            data = self._parse_json_response(response.content)
        except (LLMError, ValueError, json.JSONDecodeError, TypeError) as exc:
            self.last_error = self._format_error(exc)
            return fallback
        if not isinstance(data, dict):
            return fallback
        content = str(data.get("suggested_content") or data.get("suggested_title") or "").strip()
        if not content:
            return fallback
        warnings = data.get("warnings")
        return {
            "suggested_content": content[:2000],
            "suggested_category": str(data.get("suggested_category") or payload.get("category") or "")[:128] or None,
            "suggested_estimated_minutes": self._safe_minutes(
                data.get("suggested_estimated_minutes"),
                default=fallback["suggested_estimated_minutes"],
            ),
            "suggested_priority": self._safe_priority(data.get("suggested_priority")),
            "reason": str(data.get("reason") or fallback["reason"])[:1000],
            "warnings": [str(item)[:300] for item in warnings[:5]] if isinstance(warnings, list) else [],
        }

    def supplement_tasks(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        fallback = self._fallback_supplement(payload)
        self.last_error = None
        try:
            response = self.llm_client.generate(
                [
                    LLMMessage(
                        role="system",
                        content=(
                            "你是学习任务补充助手。你只能基于用户已有任务、近期完成情况和当天可用时间给建议。"
                            "不要调用或假设外部知识库内容。必须输出 JSON。"
                        ),
                    ),
                    LLMMessage(
                        role="user",
                        content=(
                            "请给出 1-3 个当天任务补充建议。不要直接创建任务。"
                            "输出 JSON：{suggestions:[{content,category,task_type,estimated_minutes,"
                            "priority,reason,confidence,risk_level}]}。\n"
                            f"输入：{json.dumps(payload, ensure_ascii=False, default=str)}"
                        ),
                    ),
                ]
            )
            data = self._parse_json_response(response.content)
        except (LLMError, ValueError, json.JSONDecodeError, TypeError) as exc:
            self.last_error = self._format_error(exc)
            return fallback
        suggestions = data.get("suggestions") if isinstance(data, dict) else None
        if not isinstance(suggestions, list):
            return fallback
        normalized: list[dict[str, Any]] = []
        for item in suggestions:
            if not isinstance(item, dict) or not item.get("content"):
                continue
            normalized.append(
                {
                    "content": str(item.get("content"))[:2000],
                    "category": str(item.get("category") or "")[:128] or None,
                    "task_type": str(item.get("task_type") or "")[:64] or None,
                    "estimated_minutes": self._safe_minutes(item.get("estimated_minutes"), default=45),
                    "priority": self._safe_priority(item.get("priority")),
                    "reason": str(item.get("reason") or "")[:1000],
                    "source_type": "ai_supplement",
                    "confidence": self._safe_float(item.get("confidence")),
                    "risk_level": item.get("risk_level") if item.get("risk_level") in {"low", "medium", "high"} else "medium",
                }
            )
        max_new_tasks = int(payload.get("max_new_tasks") or 3)
        return normalized[:max_new_tasks] or fallback

    @staticmethod
    def _parse_json_response(content: str) -> Any:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        if not text.startswith("{"):
            match = re.search(r"\{.*\}", text, flags=re.S)
            if not match:
                raise ValueError("LLM response does not contain JSON")
            text = match.group(0)
        return json.loads(text)

    @classmethod
    def _fallback_optimize(cls, payload: dict[str, Any]) -> dict[str, Any]:
        raw = str(payload.get("raw_content") or payload.get("raw_title") or "学习任务").strip()
        category = str(payload.get("category") or "").strip() or None
        minutes = cls._safe_minutes(payload.get("estimated_minutes"), default=60)
        if not any(word in raw for word in ["完成", "整理", "复盘", "练习", "修改", "阅读", "记录"]):
            raw = f"完成{category or ''}{raw}".strip()
        return {
            "suggested_content": raw[:2000],
            "suggested_category": category,
            "suggested_estimated_minutes": minutes,
            "suggested_priority": cls._safe_priority(payload.get("priority")),
            "reason": "模型不可用时，系统按任务内容、分类和预计用时生成可执行表达建议。",
            "warnings": ["这是规则兜底建议，请在保存前人工确认。"],
        }

    @classmethod
    def _fallback_supplement(cls, payload: dict[str, Any]) -> list[dict[str, Any]]:
        available_minutes = cls._safe_minutes(payload.get("available_minutes"), default=120)
        today_tasks = [task for task in payload.get("today_tasks", []) if isinstance(task, dict)]
        used_minutes = sum(cls._safe_minutes(task.get("estimated_minutes"), default=0) for task in today_tasks)
        if used_minutes >= int(available_minutes * 0.9):
            return []
        remaining = max(available_minutes - used_minutes, 15)
        recent_tasks = [task for task in payload.get("recent_tasks", []) if isinstance(task, dict)]
        candidates = [
            task for task in recent_tasks
            if task.get("status") in {"delayed", "pending", "in_progress"}
        ]
        suggestions: list[dict[str, Any]] = []
        for task in candidates[: int(payload.get("max_new_tasks") or 3)]:
            if remaining < 15:
                break
            minutes = min(cls._safe_minutes(task.get("estimated_minutes"), default=45), remaining, 90)
            suggestions.append(
                {
                    "content": f"继续推进：{task.get('content') or '未完成任务'}",
                    "category": task.get("category"),
                    "task_type": task.get("task_type") or "practice",
                    "estimated_minutes": minutes,
                    "priority": cls._safe_priority(task.get("priority")),
                    "reason": "根据近期未完成或进行中的任务给出补充建议，需要用户确认后创建。",
                    "source_type": "ai_supplement",
                    "confidence": 0.6,
                    "risk_level": "medium",
                }
            )
            remaining -= minutes
        if suggestions:
            return suggestions
        if remaining >= 30:
            return [
                {
                    "content": "整理今日学习复盘，记录完成情况、阻塞点和下一步最小动作。",
                    "category": "复盘",
                    "task_type": "review",
                    "estimated_minutes": min(30, remaining),
                    "priority": "medium",
                    "reason": "当天仍有可用时间且缺少可直接推进的历史任务，建议安排轻量复盘。",
                    "source_type": "ai_supplement",
                    "confidence": 0.5,
                    "risk_level": "low",
                }
            ]
        return []

    @staticmethod
    def _format_error(exc: Exception) -> str:
        message = str(exc).strip()
        return f"{exc.__class__.__name__}: {message}"[:500] if message else exc.__class__.__name__

    @staticmethod
    def _safe_minutes(value: Any, *, default: int) -> int:
        try:
            minutes = int(value)
        except (TypeError, ValueError):
            return default
        return min(max(minutes, 0), 10000)

    @staticmethod
    def _safe_priority(value: Any) -> str:
        return value if value in {"low", "medium", "high", "urgent"} else "medium"

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return min(max(number, 0.0), 1.0)
