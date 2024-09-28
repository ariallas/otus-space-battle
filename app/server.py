from datetime import timedelta
from queue import Queue
from typing import override

from loguru import logger

from app.core.command import ICommand, MacroCommand
from app.core.ioc import IoC
from app.game.setup.state import ioc_setup_event_loop, ioc_setup_exception_handler_store
from app.game.state.event_loop import (
    EventLoop,
    HardStopEventLoopCommand,
    RunEventLoopInThreadCommand,
)
from app.game.state.exception_handlers import DelayedCommand, InjectableCommand
from app.game.state.game_command import GameCommand

EVENT_LOOP_COUNT = 3


class Server:
    def __init__(self, event_loop_count: int = EVENT_LOOP_COUNT) -> None:
        self._event_loop_count = event_loop_count
        self._event_loops: dict[int, EventLoop] = {}

        self._last_game_id: int = -1
        self._gameid_to_eventloop: dict[int, EventLoop] = {}

    def start(self) -> None:
        ioc_setup_exception_handler_store()

        IoC[ICommand].resolve(
            "IoC.Scope.Register",
            "Server",
            lambda: self,
        ).execute()

        for i in range(self._event_loop_count):
            el_scope = IoC.resolve("IoC.Scope.Create", f"EventLoop {i}")
            IoC[ICommand].resolve("IoC.Scope.Current.Set", el_scope).execute()

            ioc_setup_event_loop()
            event_loop = IoC[EventLoop].resolve("EventLoop")
            self._event_loops[i] = event_loop
            IoC[ICommand].resolve("IoC.Scope.Current.Clear").execute()

            RunEventLoopInThreadCommand(event_loop, el_scope).execute()

    def stop(self) -> None:
        for event_loop in self._event_loops.values():
            event_loop.put_command(HardStopEventLoopCommand(event_loop))

    def new_game(self) -> int:
        self._last_game_id += 1
        game_id = self._last_game_id

        event_loop_id = game_id % self._event_loop_count
        event_loop = self._event_loops[event_loop_id]
        self._gameid_to_eventloop[game_id] = event_loop
        logger.info(f"Assigning game {game_id} to event loop {event_loop_id}")

        new_game_command = NewGameCommand(game_id)
        event_loop.put_command(new_game_command)

        return game_id


class NewGameCommand(ICommand):
    def __init__(self, game_id: int) -> None:
        self._game_id = game_id

    @override
    def execute(self) -> None:
        logger.info(f"Creating game {self._game_id}")

        scope = IoC.resolve("IoC.Scope.Create", f"Game {self._game_id}")
        event_loop = IoC[EventLoop].resolve("EventLoop")

        def init() -> None:
            pass

        game_command = GameCommand(
            id_=self._game_id,
            queue=Queue(),
            quant=timedelta(seconds=1),
            scope=scope,
            init=init,
        )

        injectable_delayed_command = InjectableCommand()
        repeating_game_command = MacroCommand(
            [
                game_command,
                injectable_delayed_command,
            ]
        )
        injectable_delayed_command.set_cmd(DelayedCommand(repeating_game_command))

        event_loop.put_command(repeating_game_command)
