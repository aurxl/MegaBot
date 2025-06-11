import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from megabot.settings import settings
from typing import Union

logger = logging.getLogger(__package__)
dlogger = logging.getLogger('discord')

def setup_logging() -> None:
    logger.setLevel(logging.DEBUG)
    dlogger.setLevel(logging.DEBUG)

    if not os.path.exists(settings.logging.path):
        try:
            os.mkdir(settings.logging.path)
        except Exception as exc:
            raise Exception(f"cant create directory {settings.logging.path}") from exc

    file_logger()
    stream_logger()
    discord_file_logger()

def file_logger() -> None:
    file_handler: RotatingFileHandler = RotatingFileHandler(
        filename=f"{settings.logging.path}/megabot.log",
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=7
    )

    date_format_file: str = "%Y-%m-%d %H:%M:%S"
    file_formatter: logging.Formatter = logging.Formatter(
        "[{asctime}] {levelname:<8} -> {name}: {message}",
        datefmt=date_format_file,
        style="{"
    )
    file_handler.setFormatter(file_formatter)

    if settings.logging.debug:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)

def stream_logger() -> None:
    # Initialize stream logging
    stream_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)

    date_format_stream: str = "%H:%M:%S"
    stream_formatter: logging.Formatter = logging.Formatter(
        "[{asctime}] {levelname:<8} -> {name}: {message}",
        datefmt=date_format_stream,
        style="{"
    )

    stream_handler.setFormatter(stream_formatter)

    # Determine logging level for stream handler
    if settings.logging.cli.level == 0:
        stream_handler.setLevel(logging.WARNING)
    elif settings.logging.cli.level == 1:
        stream_handler.setLevel(logging.INFO)
    elif settings.logging.cli.level == 2:
        stream_handler.setLevel(logging.DEBUG)

    logger.addHandler(stream_handler)
    dlogger.addHandler(stream_handler)

def discord_file_logger() -> None:
    file_handler: logging.handlers.RotatingFileHandler = logging.handlers.RotatingFileHandler(
        filename=f"{settings.logging.path}/discord.log",
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )

    dt_fmt: str = '%Y-%m-%d %H:%M:%S'
    formatter: logging.Formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    file_handler.setFormatter(formatter)

    if settings.logging.debug:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.INFO)

    dlogger.addHandler(file_handler)
