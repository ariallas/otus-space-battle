from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.command import ICommand
from app.core.ioc import IoC
from app.game_server import auth, endpoint
from app.game_server.server import Server


@pytest.fixture(autouse=True)
def _setup_auth() -> None:
    auth.ioc_setup_jwt_decoder()


@pytest.fixture(autouse=True)
def _setup_mock_server() -> None:
    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "Server",
        lambda: MagicMock(spec_set=Server),
    ).execute()


class JWTEncoder:
    def __init__(self, key_path: str) -> None:
        self._private_key = Path(key_path).read_text()

    def encode(self, content: dict[str, Any]) -> str:
        return jwt.encode(content, self._private_key, algorithm="RS256")


encoder = JWTEncoder("keys/private.pem")
encoder_another_key = JWTEncoder("keys/private_another.pem")

app = endpoint.make_fastapi_app(enable_auth=True)
endpoint_client = TestClient(app)


def test_correct_token() -> None:
    token = encoder.encode({"game_id": 0, "login": "user1"})

    response = endpoint_client.post("/game/0", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_wrong_game() -> None:
    token = encoder.encode({"game_id": 1, "login": "user1"})

    response = endpoint_client.post("/game/0", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_no_token() -> None:
    response = endpoint_client.post("/game/0")
    assert response.status_code == 403


def test_wrong_signature() -> None:
    token = encoder_another_key.encode({"game_id": 0, "login": "user1"})

    response = endpoint_client.post("/game/0", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
