import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect


class KitchenConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_order(self, order_data: dict):
        message = json.dumps({
            "event": "NEW_ORDER",
            "order": order_data
        })
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)


kitchen_manager = KitchenConnectionManager()
