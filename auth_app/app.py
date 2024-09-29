from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from loguru import logger
from pydantic import BaseModel


class JWTEncoder:
    def __init__(self) -> None:
        self._private_key = Path("keys/private.pem").read_text()

    def encode(self, content: dict[str, Any]) -> str:
        return jwt.encode(content, self._private_key, algorithm="RS256")


class GameIDGenerator:
    def __init__(self) -> None:
        self._last_game_id: int = -1

    def generate(self) -> int:
        self._last_game_id += 1
        return self._last_game_id


class GameParticipantStore:
    def __init__(self) -> None:
        self._participants: dict[int, list[str]] = {}

    def register_game(self, game_id: int, participants: list[str]) -> None:
        self._participants[game_id] = participants

    def check_participant(self, game_id: int, participant: str) -> bool:
        return (game_id in self._participants) and (participant in self._participants[game_id])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.jwt_encoder = JWTEncoder()
    app.state.game_id_generator = GameIDGenerator()
    app.state.participant_store = GameParticipantStore()
    yield


def jwt_encoder_dep(request: Request) -> JWTEncoder:
    return request.app.state.jwt_encoder


def game_id_generator_dep(request: Request) -> GameIDGenerator:
    return request.app.state.game_id_generator


def participant_store_dep(request: Request) -> GameParticipantStore:
    return request.app.state.participant_store


app = FastAPI(
    title="Space Battle Authorization Server",
    lifespan=lifespan,
)


class NewGameRequest(BaseModel):
    participants: list[str]


class NewGameResponse(BaseModel):
    game_id: int


@app.post("/new-game")
def new_game(
    request: NewGameRequest,
    game_id_generator: Annotated[GameIDGenerator, Depends(game_id_generator_dep)],
    participant_store: Annotated[GameParticipantStore, Depends(participant_store_dep)],
) -> NewGameResponse:
    game_id = game_id_generator.generate()
    logger.info(f"Creating a new game {game_id=} with logins: {request.participants}")
    participant_store.register_game(game_id, request.participants)
    return NewGameResponse(game_id=game_id)


class TokenRequest(BaseModel):
    game_id: int
    login: str


class TokenResponse(BaseModel):
    token: str


@app.post("/token")
def token(
    request: TokenRequest,
    participant_store: Annotated[GameParticipantStore, Depends(participant_store_dep)],
    jwt_encoder: Annotated[JWTEncoder, Depends(jwt_encoder_dep)],
) -> TokenResponse:
    if not participant_store.check_participant(request.game_id, request.login):
        raise HTTPException(status_code=401, detail="Not authorized")

    token = jwt_encoder.encode(
        {
            "login": request.login,
            "game_id": request.game_id,
        }
    )

    return TokenResponse(token=token)
