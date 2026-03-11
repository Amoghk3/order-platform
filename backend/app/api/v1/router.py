from fastapi import APIRouter

from .endpoints import auth, users, orders, rbac, health

router = APIRouter()

ROUTERS = [
    (health.router, "/health", ["Health"]),
    (auth.router, "/auth", ["Authentication"]),
    (users.router, "/users", ["Users"]),
    (orders.router, "/orders", ["Orders"]),
    (rbac.router, "/rbac", ["RBAC"]),
]

for r, prefix, tags in ROUTERS:
    router.include_router(
        r,
        prefix=prefix,
        tags=tags,
    )