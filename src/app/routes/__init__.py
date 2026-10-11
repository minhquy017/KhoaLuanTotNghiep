from src.app.routes.system_route import router as system_router
from src.app.routes.chat_route import router as chat_router
from src.app.routes.itinerary_route import router as itinerary_router
from src.app.routes.kg_route import router as kg_router

__all__ = [
    "system_router",
    "chat_router",
    "itinerary_router",
    "kg_router"
]
