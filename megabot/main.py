#!/usr/bin/env python

import asyncio
import logging
import signal
import os
import pathlib

from megabot.megabot import MegaBot
from megabot.settings import settings

logger = logging.getLogger(__package__)


class SignalHandler:
    """custom signal handler

    Especially when gmu is running as a systemd service,
    handling signals come in handy. When you want to
    manually stop the service eg. with `systemctl stop gmu`
    systemd is sending a SIGTERM signal to that process.
    With the build-in signal lib we can catch those signals
    and perform actions such as turning off the displays etc.

    Note: SIGKILL signals cant be catched by the process itself
    """
    def __init__(self, bot) -> None:
        self.bot = bot
        self.loop = bot.loop or asyncio.get_event_loop()

        signal.signal(signal.SIGTERM, self.on_shutdown)
        signal.signal(signal.SIGINT, self.on_shutdown)
    
    def on_shutdown(self, _signo, _stack_frame):
        logger.info("MegaBot shutting down")
        self.loop.create_task(self.shutdown())    

    async def shutdown(self):
        await self.bot.close()
        # await self.bot.close()


async def on_shutdown(bot) -> None:
    await bot.close()
    logger.info("MegaBot shutting down")

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
    # SignalHandler(bot=megabot)
    asyncio.run(load_modules(megabot))
    megabot.activate()

if __name__ == "__main__":
    main()
