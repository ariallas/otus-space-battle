from collections.abc import Callable

from app.command import ICommand

CommandType = type[ICommand]
ExceptionType = type[Exception]
HandlerFactoryType = Callable[[ICommand, Exception], ICommand]


class NoSuitableExceptionHandlerError(Exception):
    def __init__(self, cmd: ICommand, exc: Exception) -> None:
        super().__init__(
            f"No suitable exception handler found for Command: {cmd} and Exception: {exc}"
        )


class ExceptionHandlerStore:
    def __init__(self) -> None:
        self._handlers: dict[
            CommandType,
            dict[ExceptionType, HandlerFactoryType],
        ] = {}

        self._default_command_handlers: dict[
            CommandType,
            HandlerFactoryType,
        ] = {}

        self._default_exception_handlers: dict[
            ExceptionType,
            HandlerFactoryType,
        ] = {}

        self._default_handler: HandlerFactoryType | None = None

    def create_handler_command(self, cmd: ICommand, exc: Exception) -> ICommand:
        handler = (
            self._handlers.get(type(cmd), {}).get(type(exc), None)
            or self._default_exception_handlers.get(type(exc), None)
            or self._default_command_handlers.get(type(cmd), None)
            or self._default_handler
        )
        if not handler:
            raise NoSuitableExceptionHandlerError(cmd, exc)

        return handler(cmd, exc)

    def register_handler(
        self, ct: CommandType, et: ExceptionType, handler: HandlerFactoryType
    ) -> None:
        self._handlers.setdefault(ct, {})[et] = handler

    def register_default_command_handler(
        self, ct: CommandType, handler: HandlerFactoryType
    ) -> None:
        self._default_command_handlers[ct] = handler

    def register_default_exception_handler(
        self, et: ExceptionType, handler: HandlerFactoryType
    ) -> None:
        self._default_exception_handlers[et] = handler

    def register_default_handler(self, handler: HandlerFactoryType) -> None:
        self._default_handler = handler
