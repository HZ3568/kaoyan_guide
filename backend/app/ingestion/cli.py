from __future__ import annotations

import argparse
import json

from app.core.database import SessionLocal
from app.ingestion.pipeline import DocumentImportOptions, DocumentImportPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Import local documents into MySQL and generate chunks.")
    parser.add_argument("path", help="File or directory path under LOCAL_IMPORT_ROOT/DATA_DIR.")
    parser.add_argument("--user-id", type=int, default=None)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--source", default=None)
    parser.add_argument("--subject", default=None)
    parser.add_argument("--school", default=None)
    parser.add_argument("--major", default=None)
    parser.add_argument("--tag", action="append", dest="tags", default=None)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = DocumentImportPipeline(db).import_local_path(
            args.path,
            DocumentImportOptions(
                user_id=args.user_id,
                source=args.source,
                source_type="local",
                subject=args.subject,
                school=args.school,
                major=args.major,
                tags=args.tags,
            ),
            recursive=not args.no_recursive,
        )
        payload = {
            "imported": [
                {"id": doc.id, "title": doc.title, "file_type": doc.file_type, "parse_status": doc.parse_status}
                for doc in result.imported
            ],
            "errors": result.errors,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
