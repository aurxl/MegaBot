#!/usr/bin/env python
from megabot.settings import settings
from megabot.logging import setup_logging
import logging

setup_logging()

logger = logging.getLogger('megabot')
logger.info("Start Megabot ...")
