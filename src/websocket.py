import uuid

from fastapi import APIRouter

ws = APIRouter(prefix="/ws", tags=["websocket"])

users: set[uuid.UUID] = set()

