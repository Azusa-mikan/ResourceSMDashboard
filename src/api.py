import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from src.websocket import ws
from src.util.runner import queue_runner

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

@app.get("/")
async def index(request: Request):
    return temp.TemplateResponse(
        request=request,
        name="anime.html",
        context={
            "title": "ResourceSMDashboard"
        }
    )