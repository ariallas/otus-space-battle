import uvicorn
from loguru import logger

from auth_app.app import app


def main() -> None:
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
    )
    logger.info("Stopped uvicorn server")


if __name__ == "__main__":
    main()
