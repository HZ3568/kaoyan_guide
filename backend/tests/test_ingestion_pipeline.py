import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.database import Base
from app.ingestion.pipeline import DocumentImportOptions, DocumentImportPipeline
from app.models.ocr import OcrTableRecord, OcrTask


def test_pipeline_persists_ocr_task_and_table_records(tmp_path):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()
    try:
        ocr_json = tmp_path / "table.json"
        ocr_json.write_text(
            json.dumps(
                {
                    "tables": [
                        {
                            "rows": [
                                {
                                    "院校": "清华大学",
                                    "专业": "软件工程",
                                    "考试科目": "101政治; 201英语一; 408",
                                    "分数线": "355",
                                    "招生人数": "12人",
                                }
                            ]
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        doc = DocumentImportPipeline(db).import_file(
            ocr_json,
            DocumentImportOptions(source="OCR样例", source_type="local"),
        )

        assert doc.parse_status == "parsed"
        assert db.query(OcrTask).count() == 1
        record = db.query(OcrTableRecord).one()
        assert record.school == "清华大学"
        assert record.major == "软件工程"
        assert record.enrollment_count == 12
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
