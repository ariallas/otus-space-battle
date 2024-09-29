import uvicorn
from loguru import logger

from app.core import ioc_scoped
from app.game.setup import message_handlers
from app.game.setup.adapters import ioc_setup_adapters
from app.game_server import auth, endpoint
from app.game_server.server import Server


def main() -> None:
    ioc_scoped.setup()
    ioc_setup_adapters()

    auth.ioc_setup_jwt_decoder()

    message_handlers.ioc_setup_move()

    server = Server(event_loop_count=3)
    server.start()

    app = endpoint.make_fastapi_app(enable_auth=False)
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
    logger.info("Stopped uvicorn server")

    server.stop()


if __name__ == "__main__":
    main()
