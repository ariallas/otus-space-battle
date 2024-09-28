from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI
from loguru import logger

from app.core.ioc import IoC
from app.server import Message, Server

app = FastAPI(title="Space Battle Server")


def get_server() -> Server:
    return IoC[Server].resolve("Server")


ServerDep = Annotated[Server, Depends(get_server)]


@app.post("/game")
def new_game(server: ServerDep) -> int:
    return server.new_game()


@app.post("/message")
def post_message(message: Message, server: ServerDep) -> None:
    server.receive_message(message)


def start() -> None:
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
    logger.info("Stopped uvicorn server")
