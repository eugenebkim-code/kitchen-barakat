from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.core.config import settings
from app.services.kitchen_ws import kitchen_manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/kitchen")
async def kitchen_websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    if token != settings.KITCHEN_WS_SECRET:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await kitchen_manager.connect(websocket)
    try:
        while True:
            # Keep connection open and receive optional ping messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        kitchen_manager.disconnect(websocket)
