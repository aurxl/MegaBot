#!/usr/bin/env python
from megabot.settings import settings
import logging
import atexit

logger = logging.getLogger(__package__)

def on_shutdown() -> None:
    logger.info("MegaBot shutting down")

def main() -> None:
    atexit.register(on_shutdown)

if __name__ == "__main__":
    main()
