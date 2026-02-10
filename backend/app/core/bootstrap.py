from app.core.config import settings
from app.core.logging import init_logging
from app.db.session import init_db


def bootstrap():
    """
    Runs ONCE when app starts.
    """
    init_logging(settings.LOG_LEVEL)
    init_db()
