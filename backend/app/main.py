from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.bootstrap import bootstrap

from app.api.v1.router import router as v1_router


def create_app() -> FastAPI:
    """
    Application factory.
    Initializes configuration, logging, and routes.
    """
    bootstrap()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Order Management API with Authentication",
    )

    # CORS — allow the React dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API v1
    app.include_router(
        v1_router,
        prefix="/api/v1",
    )

    return app


app = create_app()