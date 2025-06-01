import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(logging_opts):
    logger = logging.getLogger(__package__)
    logger.setLevel(logging.DEBUG)

    if not os.path.exists(logging_opts.path):
        try:
            os.mkdir(logging_opts.path)
        except Exception as exc:
            raise Exception(f"cant create directory {logging_opts.path}") from exc

    # Initialize file logging
    file_handler = RotatingFileHandler(
        filename=f"{logging_opts.path}/megabot.log",
        encoding='utf-8',
        maxBytes=32 * 1024,  # 32 KiB
        backupCount=7
    )

    # Initialize stream logging
    stream_handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    date_format_file = "%Y-%m-%d %H:%M:%S"
    date_format_stream = "%H:%M:%S"
    file_formatter = logging.Formatter(
        "[{asctime}] {levelname:<8} -> {name}: {message}",
        datefmt=date_format_file,
        style="{"
    )
    stream_formatter = logging.Formatter(
        "[{asctime}] {levelname:<8} -> {name}: {message}",
        datefmt=date_format_stream,
        style="{"
    )
    file_handler.setFormatter(file_formatter)
    stream_handler.setFormatter(stream_formatter)

    # Determine logging level for file handler
    if logging_opts.debug:
        logging.getLogger('discord.http').setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
    else:
        logging.getLogger('discord.http').setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

    # Determine logging level for stream handler
    if logging_opts.cli.level == 0:
        stream_handler.setLevel(logging.WARNING)
    elif logging_opts.cli.level == 1:
        stream_handler.setLevel(logging.INFO)
    elif logging_opts.cli.level == 2:
        stream_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
