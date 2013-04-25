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

class Writer(object):
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
        args = message.args()
        args['datetime'] = args['datetime'].strftime(self.date_format)
        line = self.format.format(**args)
        return line

## IRC ERRORS:
class NoHandlerError(NotImplementedError):
    pass

class IRCWriter(Writer):
    def __init__(self, output, tags=None, level=DEFAULT_LEVEL,
                 format=DEFAULT_FORMAT, date_format=DEFAULT_DATE_FORMAT,
                 irc_handler=None):
        Writer.__init__(self, output, tags, level, format, date_format)
        self.irc_handler = None
    
    def write(self, line):
        if self.irc_handler is None:
            raise NoHandlerError
        
        self.irc_handler.send_message(self.output, message)
    
    def add_irc_handler(self, handler):
        self.irc_handler = handler

class Message(object):
    def __init__(self, message, level=DEFAULT_LEVEL,
                 tags=None, *args, **kwargs):
        self.tags = [] if tags is None else tags
        self.raw_message = message
        self.message = message.format(*args, **kwargs)
        self.level = level
        self.datetime = datetime.datetime.now()
    
    def args(self):
        new_dict = {}
        new_dict.update(self.__dict__)
        return new_dict

class Logger(object):
    
    instances = {}
    
    def __new__(cls, name="k-eight", *args, **kwargs):
        if name in cls.instances:
            return cls.instances[name]
        else:
            new = object.__new__(cls, *args, **kwargs)
            new.name = name
            cls.instances[name] = new
            return new
    
    def __init__(self, name="k-eight", writers=None):
        if not hasattr(self, 'writers'):
            self.writers = [] if writers is None else writers
    
    def log(self, message, level=DEFAULT_LEVEL, tags=None, *args, **kwargs):
        message = Message(message, level, tags, *args, **kwargs)
        if tags is None:
            for writer in self.writers:
                if '*' in writer.tags:
                    if writer.int_level <= LEVELS.get(message.level, 0):
                        writer._do_write(message)
            tags = []
        for tag in tags:
            for writer in self.writers:
                if tag in writer.tags or '*' in writer.tags:
                    if writer.int_level <= LEVELS.get(message.level, 0):
                        writer._do_write(message)
    
    def add_writers(self, *writers):
        self.writers.extend(writers)
    
    def add_writer(self, writer):
        self.writers.append(writer)