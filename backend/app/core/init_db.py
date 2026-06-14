import logging

from app.core.config import settings
from app.core.database import Base, engine

# 导入所有模型，保证 Base.metadata 能收集到表结构
from app import models  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    """开发环境自动建表。

    后续进入正式开发阶段，建议使用 Alembic 替代 create_all。
    如果数据库尚未启动，只记录 warning，不阻断 /health 或 API 文档启动。
    """
    if not settings.AUTO_CREATE_TABLES:
        return
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # pragma: no cover
        logger.warning("Database auto-create skipped: %s", exc)
