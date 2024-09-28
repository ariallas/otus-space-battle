from app import endpoint
from app.core import ioc_scoped
from app.core.command import ICommand
from app.core.ioc import IoC
from app.game.setup.adapters import ioc_setup_adapters
from app.game.setup.state import ioc_setup_event_loop, ioc_setup_exception_handler_store
from app.game.state.event_loop import (
    EventLoop,
    RunEventLoopInThreadCommand,
    SoftStopEventLoopCommand,
)


class Server:
    def __init__(self) -> None:
        self._event_loops: dict[int, EventLoop] = {}

    def start(self) -> None:
        ioc_scoped.setup()
        ioc_setup_adapters()
        ioc_setup_exception_handler_store()
        ioc_setup_event_loop()

        event_loops: list[EventLoop] = []

        for i in range(3):
            el_scope = IoC[ioc_scoped.Scope].resolve("IoC.Scope.Create", f"EventLoop {i}")
            IoC[ICommand].resolve("IoC.Scope.Current.Set", el_scope).execute()

            ioc_setup_event_loop()
            event_loop = IoC[EventLoop].resolve("EventLoop")
            event_loops.append(event_loop)
            RunEventLoopInThreadCommand(event_loop).execute()

            IoC[ICommand].resolve("IoC.Scope.Current.Clear").execute()

        endpoint.start()

        for event_loop in event_loops:
            event_loop.put_command(SoftStopEventLoopCommand(event_loop))
