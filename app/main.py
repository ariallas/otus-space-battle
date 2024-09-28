from app import endpoint
from app.core import ioc_scoped
from app.game.setup.adapters import ioc_setup_adapters
from app.server import Server


def main() -> None:
    ioc_scoped.setup()
    ioc_setup_adapters()

    server = Server()
    server.start()
    endpoint.start()
    server.stop()


if __name__ == "__main__":
    main()
