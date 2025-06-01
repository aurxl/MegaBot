#!/usr/bin/env python

import logging
import atexit
from megabot.discord import Bot

logger = logging.getLogger(__package__)

def on_shutdown() -> None:
    logger.info("MegaBot shutting down")

def main() -> None:
    atexit.register(on_shutdown)
    megabot = Bot()
    megabot.activate()

if __name__ == "__main__":
    main()
