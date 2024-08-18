from app.core.exception_handler_store import ExceptionHandlerStore
from app.game.state.game_loop import GameLoop


class GameState:
    """
    Класс для глобального доступа состоянию игры
    """

    def __init__(self) -> None:
        self.exception_handler_store = ExceptionHandlerStore()
        self.game_loop = GameLoop(self.exception_handler_store)

    def reset(self) -> None:
        self.exception_handler_store = ExceptionHandlerStore()
        self.game_loop = GameLoop(self.exception_handler_store)


game_state = GameState()
