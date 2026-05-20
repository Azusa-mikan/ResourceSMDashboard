from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.util.wsmanager import ConnectionManager

ws = APIRouter(prefix="/ws", tags=["websocket"])

manager = ConnectionManager()

@ws.websocket("/sysinfo")
async def ws_sysinfo(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            msg = await ws.receive()
            if msg.get("type") == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)
