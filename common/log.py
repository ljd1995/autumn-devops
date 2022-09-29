import time
from pathlib import Path

from loguru import logger

t = time.strftime("%Y%m%d")
base_dir = Path(__file__).parent.parent
logger.add(
    f"{base_dir}/logs/syslog_{t}.log",
    rotation="1 days",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    compression="tar.gz",
    retention="3 days",
)


class Log(object):
    @staticmethod
    def info(msg: str) -> None:
        logger.opt(depth=1).info(msg)

    @staticmethod
    def debug(msg: str) -> None:
        logger.opt(depth=1).debug(msg)

    @staticmethod
    def warning(msg: str) -> None:
        logger.opt(depth=1).warning(msg)

    @staticmethod
    def error(msg: str) -> None:
        logger.opt(depth=1).error(msg)

    @staticmethod
    def critical(msg: str) -> None:
        logger.opt(depth=1).critical(msg)

    @staticmethod
    def exception(msg: str | Exception) -> None:
        logger.opt(depth=1).exception(msg)

    @staticmethod
    def trace(msg: str) -> None:
        logger.opt(depth=1).trace(msg)
