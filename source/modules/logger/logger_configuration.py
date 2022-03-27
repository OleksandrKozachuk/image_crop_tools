import os
import logging
from logging.handlers import TimedRotatingFileHandler


class LoggerConfigurator:
    """
    Contain common logger configuration

    Fields:
        __default_logger            - reference to default logger (root logger)
        __default_message_format    - default log message format

    """

    def __init__(self):
        """
        Create new logger configuration
        """

        self.__default_logger = logging.getLogger()
        self.__default_logger.handlers = []

        self.__default_message_format = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"

    def set_default_format(self, message_format: str):
        """
        Set default message format

        :param message_format: input format

        :return: current instance
        """

        self.__default_message_format = message_format
        return self

    def set_level_debug(self):
        """
        Set logger minimum level - debug

        :return: current instance
        """

        self.__default_logger.setLevel(logging.DEBUG)
        return self

    def set_level_info(self):
        """
        Set logger minimum level - info

        :return: current instance
        """

        self.__default_logger.setLevel(logging.INFO)
        return self

    def set_level_warning(self):
        """
        Set logger minimum level - warning

        :return: current instance
        """

        self.__default_logger.setLevel(logging.WARNING)
        return self

    def set_level(self, level):
        """
        Set custom logger minimum level

        :param level: minimum log level

        :return: current instance
        """

        self.__default_logger.setLevel(level)
        return self

    def add_console(self):
        """
        Add console handler to root logger

        :return: current instance
        """

        formatter = logging.Formatter(self.__default_message_format)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.__default_logger.addHandler(handler)
        return self

    def add_timed_rotating(self, file_dir: str = "data/logs", rotation: str = "midnight", duration: int = 1,
                           max_copy: int = 7):
        """
        Add timed rotation file handler to root logger

        :param file_dir: log file dir (optional).
                            Default - [data/logs].
        :param rotation: Log rotation type. (optional).
                            Default - [midnight]
        :param duration: log duration (optional).
                            Default - [1]
        :param max_copy: max log file copy count, to delete (optional).
                            Default - [7]

        :return: current instance
        """
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        formatter = logging.Formatter(self.__default_message_format)

        handler = TimedRotatingFileHandler(f"{file_dir}/app.log",
                                           when=rotation, interval=duration, backupCount=max_copy)
        handler.setFormatter(formatter)
        handler.suffix = "%d-%m-%Y"

        self.__default_logger.addHandler(handler)
        return self
