import os, os.path
import sys

import yaml
import log

## Constants
VITALS = {'connection': ['nick', 'server'],
          'admin':      ['owner']}

SAMPLE_CONFIG = '''
connection:
    nick: 
    server: 
    port: 6667
    password: ~
    channels:
        - 

admin:
    owner: 
    admins:
        - 
    command_key: .
    plugins_folder: "./plugins"
    use_ident: True

nickserv:
    name: 
    password:

logging:
    -
        output: stdout
        tags: ['system']
        level: INFO

modules:
    exclude:
        - "admin"
        - "logging"
'''.strip()

## Errors:
class InvalidConfigError(ValueError):
    pass

## Helper Functions:
def dir_open(file_name, mode='a', buffering=-1):
    k_dir = os.path.split(os.path.dirname(__file__))[0]
    p_dir = os.path.join(k_dir, 'logs')
    file_name = os.path.abspath(os.path.join(p_dir, file_name))
    if not os.path.isdir(p_dir):
        os.makedirs(p_dir)
    return open(file_name, mode, buffering)

## ConfigParser
class ConfigParser(object):
    def __init__(self, file):
        self._raw_conf = yaml.load(file)
        try:
            file.close()
        except AttributeError:  # Probably isn't a filetype, roll with it
            pass
        if not isinstance(self._raw_conf, dict):
            raise InvalidConfigError("No sections")
        self.connection = dict()
        self.admin = dict()
        if self._raw_conf.get('nickserv') is not None:
            self.nickserv = self._raw_conf['nickserv']
        try:
            self.connection.update(self._raw_conf['connection'])
        except KeyError:
            raise InvalidConfigError("No connection section")
        try:
            self.admin.update(self._raw_conf['admin'])
        except KeyError:
            raise InvalidConfigError("No admin section")
        
        try:
            self.modules = self._raw_conf['modules']
        except KeyError:
            self.modules = dict()
        
        logger = log.Logger('k-eight')
        try:
            writers = self._raw_conf['logging']
        except KeyError:
            writers = list()
        
        for writer in writers:
            args = {}
            if any((writer.get(i) is None) for i in ['output']):
                raise InvalidConfigError("Invalid logger in logging section")
            
            if writer['output'] in ["stdout", "stderror"]:
                args['output'] = getattr(sys, writer['output'])
                writer_type = log.Writer
            
            elif writer['output'].startswith('#'):
                args['output'] = writer['output']
                writer_type = log.IRCWriter
            
            else:
                filemode = writer.get('filemode', 'a')
                args['output'] = dir_open(writer['output'], filemode)
                writer_type = log.Writer
             
            args['tags'] = writer.get('tags', ['*'])
            args['level'] = writer.get('level', 'INFO')
            args['format'] = writer.get('format', log.DEFAULT_FORMAT)
            df = writer.get('date_format', log.DEFAULT_DATE_FORMAT)
            args['date_format'] = df
            logger.add_writer(writer_type(**args))
        
        for section in VITALS:
            for param in VITALS[section]:
                if not param in getattr(self, section):
                    text = "parameter {0} not in {1} section"
                    raise InvalidConfigError(text.format(param, section))