#!/usr/bin/env python

import asyncio
import logging
import signal
import os
import pathlib

from megabot.megabot import MegaBot
from megabot.settings import settings

logger = logging.getLogger(__package__)


async def load_modules(bot) -> None:
    for module in settings.discord.modules:
        try:
            await bot.load_extension(f"{__package__}.modules.{module}")
        except Exception as exc:
            logger.fatal(f"Failed to load module: {exc}")

def check_cookiepath() -> None:
    if settings.player.yt_dlp.cookies:
        cookiefile_path = pathlib.Path(str(settings.player.yt_dlp.cookiefile)).parent.resolve()
        if not os.path.exists(cookiefile_path):
            try:
                os.mkdir(cookiefile_path)
                logger.debug(f"created dir {cookiefile_path} for cookies")
            except Exception as exc:
                raise Exception(f"Cant create directory {cookiefile_path}") from exc

def main() -> None:
    check_cookiepath()
    megabot = MegaBot()
    asyncio.run(load_modules(megabot))
    megabot.activate()

if __name__ == "__main__":
    main()
