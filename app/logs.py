"""Configure application logger
"""

import sys
import logging

import structlog
from pythonjsonlogger.json import JsonFormatter

def configure_logging(loglevel, log_mode):
    """Настройка логгирования приложения

    Args:
        loglevel (str): Уровень логгирования для приложения.
        log_mode (str): Какой вид вывода логов применять...
            text: Текстовое логгирование предназначено для пользователей / разработчиков.
            json: Json-логгирование предназначено для парсинга с помощью системы агрегации логов.
    """

    if not loglevel:
        loglevel = logging.INFO

    if log_mode == 'json':
        log_formatter = JsonFormatter()
    elif log_mode == 'text':
        log_formatter = logging.Formatter('%(message)s')
    elif log_mode == 'standard':
        log_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        log_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(log_formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(loglevel)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )

__all__ = ['configure_logging']
