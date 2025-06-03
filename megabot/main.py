#!/usr/bin/env python

import asyncio
import logging
import atexit

from megabot.discord import Bot
from megabot.settings import settings

logger = logging.getLogger(__package__)

def on_shutdown() -> None:
    logger.info("MegaBot shutting down")

async def load_modules(bot) -> None:
    for module in settings.discord.modules:
        try:
            await bot.load_extension(f"{__package__}.modules.{module}")
        except Exception as exc:
            logger.fatal(f"Failed to load module: {exc}")

def main() -> None:
    atexit.register(on_shutdown)
    megabot = Bot()
    asyncio.run(load_modules(megabot))
    megabot.activate()

if __name__ == "__main__":
    main()
