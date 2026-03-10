from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so Alembic can discover them
import app.db.rbac_models  # noqa: F401, E402
