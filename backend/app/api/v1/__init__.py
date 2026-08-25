from fastapi import APIRouter
from app.api.v1 import auth, menu, orders, admin, ws

api_router = APIRouter(prefix="/v1")
api_router.include_router(auth.router)
api_router.include_router(menu.router)
api_router.include_router(orders.router)
api_router.include_router(admin.router)
api_router.include_router(ws.router)

