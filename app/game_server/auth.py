from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from pydantic import BaseModel

from app.core.command import ICommand
from app.core.ioc import IoC


class JWTDecoder:
    def __init__(self) -> None:
        self._public_key = Path("keys/public.pem").read_text()

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self._public_key, algorithms=["RS256"])


def ioc_setup_jwt_decoder() -> None:
    jwt_decoder = JWTDecoder()

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "JWTDecoder",
        lambda: jwt_decoder,
    ).execute()


###


security = HTTPBearer()


def get_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> str:
    return credentials.credentials


class GameToken(BaseModel):
    game_id: int
    login: str


def decode_token(token: Annotated[str, Depends(get_token)]) -> GameToken:
    decoder = IoC[JWTDecoder].resolve("JWTDecoder")
    token_dict = decoder.decode(token)
    return GameToken(**token_dict)


###

AuthorizeGameStrategy = Callable[[int, GameToken], None]


def ioc_setup_authorize_game_strategy() -> None:
    def authorize_game_strategy(game_id: int, token: GameToken) -> None:
        if game_id != token.game_id:
            raise HTTPException(401, "Not authorized")

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "AuthorizeGameStrategy",
        lambda: authorize_game_strategy,
    ).execute()


def ioc_setup_mock_authorize_game_strategy() -> None:
    def mock_authorize_game_strategy(game_id: int, token: GameToken) -> None:  # noqa: ARG001
        pass

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "AuthorizeGameStrategy",
        lambda: mock_authorize_game_strategy,
    ).execute()


def authorize_game(game_id: int, token: Annotated[GameToken, Depends(decode_token)]) -> None:
    authorize_strategy = IoC[AuthorizeGameStrategy].resolve("AuthorizeGameStrategy")
    authorize_strategy(game_id, token)
