from app import endpoint
from app.core import ioc_scoped
from app.game.setup import message_handlers
from app.game.setup.adapters import ioc_setup_adapters
from app.server import Server


def main() -> None:
    ioc_scoped.setup()
    ioc_setup_adapters()

    message_handlers.ioc_setup_move()

    server = Server(event_loop_count=3)
    server.start()
    endpoint.start()
    server.stop()


if __name__ == "__main__":
    main()
