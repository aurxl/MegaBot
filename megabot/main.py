#!/usr/bin/env python

import asyncio
import logging
import atexit

from megabot.discord import Bot
from megabot.settings import settings

logger = logging.getLogger(__package__)

def on_shutdown() -> None:
    logger.info("MegaBot shutting down")

async def load_extensions(bot) -> None:
    for cog in settings.discord.extensions:
        try:
            await bot.load_extension(f"{__package__}.commands.{cog}")
        except Exception as exc:
            logger.fatal(f"Failed to load extension: {exc}")

def main() -> None:
    atexit.register(on_shutdown)
    megabot = Bot()
    asyncio.run(load_extensions(megabot))
    megabot.activate()

if __name__ == "__main__":
    main()
