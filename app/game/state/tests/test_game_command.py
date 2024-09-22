from datetime import timedelta
from queue import Queue
from unittest.mock import MagicMock

from app.core.ioc import IoC
from app.core.ioc_scoped import Scope
from app.game.state.game_command import GameCommand


def test_game_command() -> None:
    queue = Queue()
    cmd = MagicMock()
    queue.put(cmd)

    scope = IoC[Scope].resolve("IoC.Scope.Create", "scope1")

    def init() -> None:
        pass

    game_cmd = GameCommand(queue, timedelta(seconds=1), scope, lambda: None)
    game_cmd.execute()

    cmd.execute.assert_called_once()
