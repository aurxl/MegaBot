#!/usr/bin/env python

import discord
import logging

from megabot.settings import settings

logger = logging.getLogger(__package__)

class Bot(discord.Client):
    def __init__(self, intents: discord.Intents = discord.Intents.default()):
        super().__init__(intents=intents)
        self.intents.message_content = True

    def activate(self):
        self.run(settings.discord.token, log_handler=None, root_logger=True)

    async def on_ready(self):
        logger.info(f"Logged into discord as {self.user}")

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')
