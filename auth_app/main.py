import uvicorn
from loguru import logger

from auth_app.app import app


def main() -> None:
    pass


if __name__ == "__main__":
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
    logger.info("Stopped uvicorn server")
