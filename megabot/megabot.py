#!/usr/bin/env python

import discord
import logging
import asyncio
import signal

from discord.ext import commands
from megabot.settings import settings

logger = logging.getLogger(__package__)


class SignalHandler:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.loop = bot.loop

        self.loop.add_signal_handler(signal.SIGTERM, self.on_shutdown)
        self.loop.add_signal_handler(signal.SIGINT, self.on_shutdown)

    def on_shutdown(self):
        logger.info("MegaBot shutting down")
        self.loop.create_task(self.bot.close())


class MegaBot(commands.Bot):
    def __init__(self):
        self.command_prefix = settings.discord.prefix

        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents, command_prefix=self.command_prefix)

    async def setup_hook(self):
        SignalHandler(self)

    def activate(self):
        self.run(settings.discord.token, log_handler=None, root_logger=True)

    async def on_ready(self):
        logger.debug(f"Loaded settings: {settings.as_dict()}")
        logger.info("MegaBot started!")
        logger.info(f"Logged into discord as {self.user}")

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')

        await self.process_commands(message)
