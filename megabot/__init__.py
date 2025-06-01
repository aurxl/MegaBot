#!/usr/bin/env python
from megabot.settings import settings
from megabot.logging import setup_logging
import logging

setup_logging(settings.logging)

logger = logging.getLogger('megabot')
logger.info("MegaBot started")
logger.debug(f"Loaded settings: {settings.as_dict()}")
