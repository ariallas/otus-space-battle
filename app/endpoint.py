from typing import Annotated, Any

import uvicorn
from fastapi import Depends, FastAPI
from loguru import logger
from pydantic import BaseModel

from app.core.ioc import IoC
from app.server import Server

app = FastAPI(title="Space Battle Server")


def get_server() -> Server:
    return IoC[Server].resolve("Server")


ServerDep = Annotated[Server, Depends(get_server)]


@app.post("/game")
def new_game(server: ServerDep) -> int:
    return server.new_game()


class Message(BaseModel):
    game_id: int
    object_id: int
    op_id: str
    args: dict[str, Any]


@app.post("/message")
def post_message(_message: Message) -> None:
    pass


def start() -> None:
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
    logger.info("Stopped uvicorn server")
