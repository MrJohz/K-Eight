"""A logger.  Because apparently the default one isn't good enough."""

from collections import defaultdict
import datetime

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S%z"
DEFAULT_FORMAT = "[{datetime}] {level}: {message}"
DEFAULT_LEVEL = "INFO"
NEWLINE = '\n'

LEVELS = {"NOTSET":   00,
          "DEBUG":    10,
          "INFO":     20,
          "WARNING":  30,
          "ERROR":    40,
          "CRITICAL": 50}

class Out(object):
    def __init__(self, output, tags=None, level=DEFAULT_LEVEL,
                 format=DEFAULT_FORMAT, date_format=DEFAULT_DATE_FORMAT):
        self.output = output
        self.tags = tags if tags is not None else ['*']
        self.level = level
        self.int_level = LEVELS.get(level, 0)
        self.format = format
        self.date_format = date_format
    
    def write(self, line):
        self.output.write(line)
        self.output.write(NEWLINE)
        self.output.flush()
    
    def _do_write(self, message):
        line = self._pre_write(message)
        self.write(line)
    
    def _pre_write(self, message):
        args = message.__dict__
        args['datetime'] = args['datetime'].strftime(self.date_format)
        line = self.format.format(**args)
        return line

class Message(object):
    def __init__(self, message, level=DEFAULT_LEVEL,
                 tags=None, *args, **kwargs):
        self.tags = [] if tags is None else tags
        self.raw_message = message
        self.message = message.format(*args, **kwargs)
        self.level = level
        self.datetime = datetime.datetime.now()
    
    def args(self):
        return self.__dict__

class In(object):
    
    instances = {}
    
    def __new__(cls, name="genericlumberjack", *args, **kwargs):
        if name in cls.instances:
            return cls.instances[name]
        else:
            new = object.__new__(cls, *args, **kwargs)
            new.name = name
            cls.instances[name] = new
            return new
    
    def __init__(self, name="genericlumberjack", loggers=None):
        self.loggers = [] if loggers is None else loggers
    
    def log(self, message, level=DEFAULT_LEVEL, tags=None, *args, **kwargs):
        message = Message(message, level, tags, *args, **kwargs)
        if tags is None:
            for logger in self.loggers:
                if '*' in logger.tags:
                    if logger.int_level <= LEVELS.get(message.level, 0):
                        logger._do_write(message)
        tags = []
        for tag in tags:
            for logger in self.loggers:
                if tag in logger.tags or '*' in logger.tags:
                    if logger.int_level <= LEVELS.get(message.level, 0):
                        logger._do_write(message)
    
    def add_loggers(self, *loggers):
        self.loggers.extend(loggers)