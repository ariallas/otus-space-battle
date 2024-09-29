from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from loguru import logger

from app.core.ioc import IoC
from app.game_server.auth import authorize_game
from app.game_server.server import Message, Server

app = FastAPI(title="Space Battle Server")


def get_server() -> Server:
    return IoC[Server].resolve("Server")


ServerDep = Annotated[Server, Depends(get_server)]


@app.post("/game/{game_id}", dependencies=[Depends(authorize_game)])
def new_game(game_id: int, server: ServerDep) -> int:
    return server.new_game(game_id)


@app.post("/game/{game_id}/message", dependencies=[Depends(authorize_game)])
def post_message(game_id: int, message: Message, server: ServerDep) -> None:
    if message.game_id != game_id:
        raise HTTPException(400, "Game ID is not the same in path and message")
    server.receive_message(message)


def start() -> None:
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
    logger.info("Stopped uvicorn server")
