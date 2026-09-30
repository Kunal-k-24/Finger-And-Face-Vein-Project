import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(prefix="/federated", tags=["Federated Learning"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # In a real scenario, the FL server would broadcast round updates here
            await manager.broadcast({"type": "info", "message": f"Client sent: {data}"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/trigger_round")
async def trigger_federated_round():
    """
    Triggers a federated learning round (simulation for now).
    """
    await manager.broadcast({
        "type": "round_update",
        "round": 1,
        "status": "started",
        "message": "Federated learning round 1 started across 5 clients."
    })
    return {"message": "Federated round triggered"}
