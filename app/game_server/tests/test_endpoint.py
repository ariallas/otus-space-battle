import threading
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.command import ICommand, LambdaCommand
from app.core.ioc import IoC
from app.core.ioc_scoped import Scope
from app.game_server import endpoint
from app.game_server.server import Message, Server


@pytest.fixture(autouse=True)
def server() -> Iterator[Server]:
    server = Server(event_loop_count=2)
    server.start()

    events = [threading.Event(), threading.Event()]
    for event, event_loop in zip(events, server.event_loops.values(), strict=True):
        event_loop.add_after_hook(event.set)

    yield server

    server.stop()

    for event in events:
        event.wait()


app = endpoint.make_fastapi_app(enable_auth=False)
endpoint_client = TestClient(app)


def test_endpoint() -> None:
    response = endpoint_client.post("/game/0")
    assert response.json() == 0
    response = endpoint_client.post("/game/1")
    assert response.json() == 1

    events = [threading.Event(), threading.Event()]

    def handle_test_op(message: Message) -> None:
        scope = IoC[Scope].resolve("IoC.Scope.Current")
        assert scope.name == f"Game {message.game_id}"
        events[message.game_id].set()

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "MessageHandler.test_op",
        LambdaCommand(handle_test_op).setup,
    ).execute()

    response = endpoint_client.post(
        "/game/0/message",
        json={
            "game_id": 0,
            "object_id": 0,
            "op_id": "test_op",
            "args": {},
        },
    )
    assert response.status_code == 200

    response = endpoint_client.post(
        "/game/1/message",
        json={
            "game_id": 1,
            "object_id": 0,
            "op_id": "test_op",
            "args": {},
        },
    )
    assert response.status_code == 200

    for event in events:
        event.wait()
