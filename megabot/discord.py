#!/usr/bin/env python

import discord
import logging

from discord.ext import commands
from megabot.settings import settings

logger = logging.getLogger(__package__)

class Bot(commands.Bot):
    def __init__(self):
        self.command_prefix = settings.discord.prefix

        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents, command_prefix=self.command_prefix)

    def activate(self):
        self.run(settings.discord.token, log_handler=None, root_logger=True)

    async def on_ready(self):
        logger.info(f"Logged into discord as {self.user}")

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')

        await self.process_commands(message)
