from datetime import timedelta
from queue import Queue
from typing import Any, override

from loguru import logger
from pydantic import BaseModel

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


class Message(BaseModel):
    game_id: int
    object_id: int
    op_id: str
    args: dict[str, Any]


GameQueueMap = dict[int, Queue[ICommand]]


class Server:
    def __init__(self, event_loop_count: int = EVENT_LOOP_COUNT) -> None:
        self._event_loop_count = event_loop_count
        self._event_loops: dict[int, EventLoop] = {}

        self._last_game_id: int = -1

    def start(self) -> None:
        ioc_setup_exception_handler_store()

        IoC[ICommand].resolve(
            "IoC.Scope.Register",
            "Server",
            lambda: self,
        ).execute()

        for i in range(self._event_loop_count):
            self._create_and_start_event_loop(i)

    def _create_and_start_event_loop(self, loop_id: int) -> None:
        el_scope = IoC.resolve("IoC.Scope.Create", f"EventLoop {loop_id}")
        IoC[ICommand].resolve("IoC.Scope.Current.Set", el_scope).execute()

        ioc_setup_event_loop()
        event_loop = IoC[EventLoop].resolve("EventLoop")
        self._event_loops[loop_id] = event_loop

        event_loop_game_queues: GameQueueMap = {}
        IoC[ICommand].resolve(
            "IoC.Scope.Register",
            "EventLoop.game_queues",
            lambda: event_loop_game_queues,
        ).execute()

        IoC[ICommand].resolve("IoC.Scope.Current.Clear").execute()

        RunEventLoopInThreadCommand(event_loop, el_scope).execute()

    def stop(self) -> None:
        for event_loop in self._event_loops.values():
            event_loop.put_command(HardStopEventLoopCommand(event_loop))

    def new_game(self) -> int:
        self._last_game_id += 1
        game_id = self._last_game_id

        event_loop_id = self._gameid_to_eventloopid(game_id)
        event_loop = self._event_loops[event_loop_id]
        logger.info(f"Assigning game {game_id} to event loop {event_loop_id}")

        new_game_command = NewGameCommand(game_id)
        event_loop.put_command(new_game_command)

        return game_id

    def receive_message(self, message: Message) -> None:
        event_loop_id = self._gameid_to_eventloopid(message.game_id)
        event_loop = self._event_loops[event_loop_id]

        event_loop.put_command(
            PutCommandToGameQueue(
                game_id=message.game_id,
                cmd=InterpretCommand(message),
            )
        )

    def _gameid_to_eventloopid(self, game_id: int) -> int:
        return game_id % self._event_loop_count


class NewGameCommand(ICommand):
    def __init__(self, game_id: int) -> None:
        self._game_id = game_id

    @override
    def execute(self) -> None:
        logger.info(f"Creating game {self._game_id}")

        scope = IoC.resolve("IoC.Scope.Create", f"Game {self._game_id}")
        event_loop = IoC[EventLoop].resolve("EventLoop")
        game_queue = Queue()

        def init() -> None:
            pass

        game_command = GameCommand(
            id_=self._game_id,
            queue=game_queue,
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

        # Регистрируем игру в словаре игр ивент лупа
        game_queues = IoC[GameQueueMap].resolve("EventLoop.game_queues")
        game_queues[self._game_id] = game_queue


class PutCommandToGameQueue(ICommand):
    """
    Добавляет команду в очередь конретной игры.
    Должна выполняться внутри одного EventLoop с игрой.
    """

    def __init__(self, game_id: int, cmd: ICommand) -> None:
        self._game_id = game_id
        self._cmd = cmd

    @override
    def execute(self) -> None:
        logger.debug(f"Sending command {self._cmd} to game {self._game_id}")
        game_queues = IoC[GameQueueMap].resolve("EventLoop.game_queues")
        game_queues[self._game_id].put(self._cmd)


class InterpretCommand(ICommand):
    def __init__(self, message: Message) -> None:
        self._message = message

    @override
    def execute(self) -> None:
        logger.info("Executing InterpretCommand")
        # match self._message.op_id:
        #     case "Move":
        #         obj = IoC[UObject].resolve("Game.Items", self._message.object_id)
