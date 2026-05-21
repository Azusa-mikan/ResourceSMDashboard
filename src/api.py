import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from src.websocket import ws
from src.util.runner import queue_runner, get_static_sysinfo

@asynccontextmanager
async def custom_lifespan(app: FastAPI):
    t = asyncio.create_task(queue_runner())
    try:
        yield
    finally:
        t.cancel()
        await t

app = FastAPI(lifespan=custom_lifespan)
temp = Jinja2Templates(
    directory=(Path(__file__).parent / "assets")
)
app.include_router(ws)

def static_sysinfo_to_dict():
    data = get_static_sysinfo()
    cpu = {
        "name": data.cpu.name,
        "core_count": data.cpu.core_count,
        "thread_count": data.cpu.thread_count,
    }
    mem = {
        "type": data.mem.type,
        "speed": data.mem.speed,
    }
    return {
        "cpu": cpu,
        "mem": mem,
    }

static_sysinfo_dict = static_sysinfo_to_dict()

@app.get("/")
async def index(request: Request):
    return temp.TemplateResponse(
        request=request,
        name="anime.html",
        context={
            "title": "ResourceSMDashboard"
        }
    )

@app.get("/sysinfo")
async def query_sysinfo():
    return static_sysinfo_dict