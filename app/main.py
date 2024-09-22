import uvicorn
from loguru import logger

from app.core import ioc_scoped
from app.endpoint import app
from app.game.setup.adapters import ioc_setup_adapters
from app.game.setup.state import ioc_setup_game_state


def main() -> None:
    ioc_scoped.setup()
    ioc_setup_adapters()
    ioc_setup_game_state()

    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )


if __name__ == "__main__":
    main()
