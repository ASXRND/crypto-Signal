#!/usr/bin/env python3
"""Main app module
"""
import time
import sys
import asyncio

import logs
import conf
import structlog

from conf import Configuration
from exchange import ExchangeInterface
from notification import Notifier
from behaviour import Behaviour


async def main():
    """Initializes the application"""
    # Load settings and create the config object
    config = Configuration()
    settings = config.settings

    # Set up logger
    logs.configure_logging(settings.get('log_level', 'INFO'), settings.get('log_mode', 'standard'))
    logger = structlog.get_logger()

    # Configure and run configured behaviour.
    exchange_interface = ExchangeInterface(config.exchanges)
    notifier = Notifier(config.notifiers)

    behaviour = Behaviour(
        config,
        exchange_interface,
        notifier
    )

    while True:
        settings['timeframe'] = '15m'  # Установка 15-минутного таймфрейма для всех монет
        await behaviour.run(settings['market_pairs'], settings['output_mode'])  # Добавлено await
        logger.info("Sleeping for 120 seconds")
        await asyncio.sleep(120)  # Используем asyncio.sleep для асинхронного сна

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Запуск асинхронной функции main
    except KeyboardInterrupt:
        sys.exit(0)
