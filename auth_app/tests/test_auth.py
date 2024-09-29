from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import jwt
import pytest
from fastapi.testclient import TestClient

from auth_app.app import app, lifespan


class JWTDecoder:
    def __init__(self) -> None:
        self._public_key = Path("keys/public.pem").read_text()

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self._public_key, algorithms=["RS256"])


decoder = JWTDecoder()


@pytest.fixture()
async def test_client() -> AsyncIterator[TestClient]:
    async with lifespan(app):
        yield TestClient(app)


def test_new_game(test_client: TestClient) -> None:
    response = test_client.post(
        "/new-game",
        json={
            "participants": ["user1", "user2"],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"game_id": 0}

    response = test_client.post(
        "/new-game",
        json={
            "participants": ["user1", "user2"],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"game_id": 1}


@pytest.fixture()
def game_id(test_client: TestClient) -> int:
    response = test_client.post(
        "/new-game",
        json={
            "participants": ["user1", "user2"],
        },
    )
    assert response.status_code == 200
    return response.json()["game_id"]


def test_token(game_id: int, test_client: TestClient) -> None:
    response = test_client.post(
        "/token",
        json={"game_id": game_id, "login": "user1"},
    )
    assert response.status_code == 200
    content = decoder.decode(response.json()["token"])
    assert content == {"login": "user1", "game_id": game_id}


def test_token_invlaid_login(game_id: int, test_client: TestClient) -> None:
    response = test_client.post(
        "/token",
        json={"game_id": game_id, "login": "another_user"},
    )
    assert response.status_code == 401


def test_token_invalid_game(test_client: TestClient) -> None:
    response = test_client.post(
        "/token",
        json={"game_id": 99999, "login": "user1"},
    )
    assert response.status_code == 401
