__all__ = [
    "system_router",
    "ALL_ROUTERS"
]

from .system import router as system_router

ALL_ROUTERS = [
    system_router,
]
