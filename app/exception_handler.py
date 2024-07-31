from collections.abc import Callable

from app.command import ICommand

CommandType = type[ICommand]
ExceptionType = type[Exception]
HandlerFactoryType = Callable[[ICommand, Exception], ICommand]


class ExceptionHandlerStore:
    def __init__(self) -> None:
        self._handlers: dict[
            CommandType,
            dict[ExceptionType, HandlerFactoryType],
        ] = {}

        # self.default_command_handlers: dict[
        #     CommandType,
        #     HandlerFactoryType,
        # ] = {}

    def create_handler(self, cmd: ICommand, exc: Exception) -> ICommand:
        return self._handlers[type(cmd)][type(exc)](cmd, exc)

    def register_handler(
        self, ct: CommandType, et: ExceptionType, handler: HandlerFactoryType
    ) -> None:
        self._handlers.setdefault(ct, {})[et] = handler
