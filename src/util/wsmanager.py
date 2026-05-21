import asyncio

from fastapi import WebSocket
from src.util.databus import sysque
from src.util.sysdataclass import DynamicSysteminfo

def payload_json(sysinfo: DynamicSysteminfo):
    cpu = {
        "usage": sysinfo.cpu.usage,
        "clock": sysinfo.cpu.clock,
        "temperature": sysinfo.cpu.temperature,
    }
    mem = {
        "total": sysinfo.mem.total,
        "available": sysinfo.mem.available,
        "used": sysinfo.mem.used,
    }
    return {
        "cpu": cpu,
        "mem": mem,
    }

class ConnectionManager:
    def __init__(self) -> None:
        self.connset: set[WebSocket] = set()
        self.task = None
        self.lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connset.add(ws)
        async with self.lock:
            if self.connset and (self.task is None or self.task.done()):
                self.task = asyncio.create_task(
                    self.broadcast()
                )
    
    def disconnect(self, ws: WebSocket):
        self.connset.discard(ws)
        if not self.connset and self.task is not None:
            if not self.task.done():
                self.task.cancel()
            self.task = None
    
    async def broadcast(self):
        while True:
            try:
                sysinfo = await sysque.get()
                conns = list(self.connset)
                # 并发向所有连接发送数据，提升广播效率
                results = await asyncio.gather(
                    *[c.send_json(payload_json(sysinfo)) for c in conns],
                    return_exceptions=True,
                )
                for c, r in zip(conns, results):
                    if isinstance(r, BaseException):
                        self.disconnect(c)
            except asyncio.CancelledError:
                return
            except Exception:
                continue

