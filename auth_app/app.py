from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

app = FastAPI(title="Space Battle Authorization Server")


class NewGameRequest(BaseModel):
    logins: list[str]


class NewGameResponse(BaseModel):
    token: str
    game_id: int


last_game_id: int = -1


def generate_game_id() -> int:
    global last_game_id  # noqa: PLW0603
    last_game_id += 1
    return last_game_id


@app.post("/token")
def token(request: NewGameRequest) -> NewGameResponse:
    game_id = generate_game_id()
    logger.info(f"Creating a new game {game_id=} with logins: {request.logins}")
    return NewGameResponse(token="123", game_id=game_id)
