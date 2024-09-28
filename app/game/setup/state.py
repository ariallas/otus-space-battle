from app.core.command import ICommand
from app.core.exception_handler_store import ExceptionHandlerStore
from app.core.ioc import IoC
from app.game.state.event_loop import EventLoop


def ioc_setup_exception_handler_store() -> None:
    exception_handler_store = ExceptionHandlerStore()

    def _get_exception_handler_store() -> ExceptionHandlerStore:
        return exception_handler_store

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "ExceptionHandlerStore",
        _get_exception_handler_store,
    ).execute()


def ioc_setup_event_loop() -> None:
    exception_handler_store = IoC[ExceptionHandlerStore].resolve("ExceptionHandlerStore")
    event_loop = EventLoop(exception_handler_store)

    def _get_event_loop() -> EventLoop:
        return event_loop

    IoC[ICommand].resolve(
        "IoC.Scope.Register",
        "EventLoop",
        _get_event_loop,
    ).execute()
