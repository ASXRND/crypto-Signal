""" Utilities for notifiers
"""

import re
import structlog

class NotifierUtils():
    """ Utilities for notifiers
    """

    def __init__(self):
        self.logger = structlog.get_logger()

    def clean_message(self, message):
        """Удаляет множественные пробелы и лишние пустые строки из строки"""
        # Удаляем множественные пробелы
        message = re.sub(r'[ \t]+', ' ', message)
        # Удаляем более одной пустой строки подряд
        message = re.sub(r'\n{3,}', '\n\n', message)
        # Удаляем пробелы в начале и конце строк
        message = '\n'.join(line.strip() for line in message.splitlines())
        # Удаляем пустые строки в начале и конце сообщения
        return message.strip()

    def chunk_message(self, message, max_message_size):
        """ Chunks message so that it meets max size of integration.

        Args:
            message (str): The message to chunk.
            max_message_size (int): The max message length for the chunks.

        Returns:
            list: The chunked message.
        """
        # Очищаем сообщение перед разбиением
        message = self.clean_message(message)
        chunked_message = list()
        if len(message) > max_message_size:
            split_message = message.splitlines(keepends=True)
            chunk = ''

            for message_part in split_message:
                temporary_chunk = chunk + message_part

                if max_message_size > len(temporary_chunk):
                    chunk += message_part
                else:
                    chunked_message.append(chunk)
                    chunk = ''
            if chunk:
                chunked_message.append(chunk)
        else:
            chunked_message.append(message)

        return chunked_message
