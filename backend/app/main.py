from fastapi import FastAPI

from app.core.config import settings
from app.core.bootstrap import bootstrap

from app.api.v1 import health
from app.api.v1 import users
from app.api.v1 import orders
from app.api.v1 import auth


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

    # Register routers
    app.include_router(
        health.router,
        prefix="/api/v1",
        tags=["Health"],
    )

    app.include_router(
        auth.router,
        prefix="/api/v1/auth",
        tags=["Authentication"],
    )

    app.include_router(
        users.router,
        prefix="/api/v1/users",
        tags=["Users"],
    )

    app.include_router(
        orders.router,
        prefix="/api/v1/orders",
        tags=["Orders"],
    )

    return app


app = create_app()