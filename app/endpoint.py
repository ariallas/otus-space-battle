from typing import Any

import uvicorn
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

app = FastAPI(title="Space Battle Server")


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
