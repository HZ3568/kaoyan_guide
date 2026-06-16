from __future__ import annotations

import argparse
import json

from app.core.database import SessionLocal
from app.ingestion.pipeline import DocumentImportOptions, DocumentImportPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Import local documents into MySQL and generate generic chunks.")
    parser.add_argument("path", help="File or directory path under LOCAL_IMPORT_ROOT/DATA_DIR.")
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument("--knowledge-base-id", type=int, default=None)
    parser.add_argument("--goal-id", type=int, default=None)
    parser.add_argument("--domain", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--tag", action="append", dest="tags", default=None)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = DocumentImportPipeline(db).import_local_path(
            args.path,
            DocumentImportOptions(
                user_id=args.user_id,
                knowledge_base_id=args.knowledge_base_id,
                goal_id=args.goal_id,
                domain=args.domain,
                category=args.category,
                tags=args.tags,
            ),
            recursive=not args.no_recursive,
        )
        payload = {
            "imported": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "parse_status": doc.parse_status,
                    "chunk_count": doc.chunk_count,
                }
                for doc in result.imported
            ],
            "errors": result.errors,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
