from loguru import logger
import sys


def init_logging(level: str):
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        format="{time} | {level} | {message}",
    )
