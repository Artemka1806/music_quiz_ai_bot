__all__ = [
    "system_router",
    "ALL_ROUTERS"
]

from .system import router as system_router
from .quiz import router as quiz_router

ALL_ROUTERS = [
    system_router,
    quiz_router
]
