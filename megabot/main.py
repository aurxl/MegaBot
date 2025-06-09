#!/usr/bin/env python

import asyncio
import logging
import signal
import os
import pathlib as p

from megabot.megabot import MegaBot
from megabot.settings import settings

logger = logging.getLogger(__package__)

async def load_modules(bot:MegaBot) -> None:
    for module in settings.modules.keys():
        try:
            if settings.modules[module].enabled:
                await bot.load_extension(f"{__package__}.modules.{module}")
        except Exception as exc:
            logger.fatal(f"Failed to load module: {exc}")

def create_directories() -> None:
    directories = [
        p.Path(str(settings.logging.path)),
        p.Path(str(settings.megabot.datapath)),
    ]
    if settings.modules.music.enabled:
        if not settings.modules.music.mediapath:
            settings.modules.music.mediapath = str(p.Path(str(settings.megabot.datapath) + "/media_cache"))
        directories.append(p.Path(str(settings.modules.music.mediapath)))

    if settings.modules.music.yt_dlp.cookies:
        if not settings.modules.music.yt_dlp.cookiefile:
            settings.modules.music.yt_dlp.cookiefile = str(p.Path(str(settings.megabot.datapath) + "/cookies")) + "/cookies.txt"
        cookiefile_path = p.Path(str(settings.modules.music.yt_dlp.cookiefile)).parent.resolve()
        directories.append(cookiefile_path)

    for dir in directories:
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
                logger.debug(f"created directory {dir}")
            except Exception as exc:
                msg = f"Can't create directory {dir}: {exc}"
                logger.debug(msg)
                raise Exception(msg) from exc

def main() -> None:
    create_directories()
    megabot = MegaBot()
    asyncio.run(load_modules(megabot))
    megabot.activate()

if __name__ == "__main__":
    main()
