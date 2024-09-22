from typing import Any

from fastapi import FastAPI
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
