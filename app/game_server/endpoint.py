from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException

from app.core.ioc import IoC
from app.game_server.auth import authorize_game
from app.game_server.server import Message, Server


def make_fastapi_app(*, enable_auth: bool) -> FastAPI:
    app = FastAPI(title="Space Battle Server")

    game_router_deps = [Depends(authorize_game)] if enable_auth else []
    app.include_router(gamerouter, prefix="/game/{game_id}", dependencies=game_router_deps)
    return app


def get_server() -> Server:
    return IoC[Server].resolve("Server")


ServerDep = Annotated[Server, Depends(get_server)]

gamerouter = APIRouter()


@gamerouter.post("")
def new_game(game_id: int, server: ServerDep) -> int:
    return server.new_game(game_id)


@gamerouter.post("/message")
def post_message(game_id: int, message: Message, server: ServerDep) -> None:
    if message.game_id != game_id:
        raise HTTPException(400, "Game ID is not the same in path and message")
    server.receive_message(message)
