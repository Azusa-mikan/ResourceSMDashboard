from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from src.websocket import ws

app = FastAPI()
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