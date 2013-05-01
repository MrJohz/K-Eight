import imp
import os

from log import Logger

DEF_PLUGIN_FOLDER = './plugins'
COMMAND_STARTS = ['do_',    # for a normal .command
                  're_',    # regular expression comand
                  'clock_', # clock command
                  'cmd_'    # IRC command
                  ]

COMMAND_NAMES = ['command',
                 're',
                 'clock',
                 'cmd'
                 ]

logger = Logger()

def get_plugins(plugin_folder=DEF_PLUGIN_FOLDER):
    plugin_folder = DEF_PLUGIN_FOLDER if plugin_folder is None else plugin_folder
    possiblePlugins = os.listdir(plugin_folder)
    for item in possiblePlugins:
        location = os.path.join(plugin_folder, item)
        if not os.path.isfile(location) or not location.endswith('.py'):
            continue
        name = item[:-3]
        info = imp.find_module(name, [os.path.abspath(plugin_folder)])
        yield {'name':name, 'info':info}

def load_plugin(plugin):
    try:
        return imp.load_module(plugin['name'], *plugin['info'])
    except ImportError as exc:
        msg = "Failed to load module {modname}: {exc!s}"
        logger.warning(msg, tags=['system'], modname=plugin['name'], exc=exc)
        return None

def get_funcs(plugin_folder=DEF_PLUGIN_FOLDER, name=None, module_config=None):
    module_config = {} if module_config is None else module_config
    if name is None:
        for plugin in get_plugins(plugin_folder):
            if module_config.get('include') is not None:
                if not plugin['name'] in module_config['include']:
                    continue
            elif plugin['name'] in module_config.get('exclude', []):
                continue
            
            plug = load_plugin(plugin)
            if plug is None:
                continue
            for j, k in vars(plug).items():
                if isinstance(k, PluginFunction):
                    k.add_module(plugin['name'])
                    yield k
                elif callable(k) and any(map(j.startswith, COMMAND_STARTS)):
                    k.__name__ = j    # not always guaranteed.
                    yield PluginFunction(k, plugin['name'])
    else:
        for plugin in get_plugins(plugin_folder):
            if module_config.get('include') is not None:
                if not plugin['name'] in module_config['include']:
                    continue
            elif plugin['name'] in module_config.get('exclude', []):
                continue
            
            if plugin['name'] == name:
                plug = load_plugin(plugin)
                if plug is None:
                    break
                for j, k in vars(plug).items():
                    if isinstance(k, PluginFunction):
                        k.add_module(plugin['name'])
                        yield k
                    elif callable(k) and any(map(j.startswith, COMMAND_STARTS)):
                        k.__name__ = j   # not always guaranteed.
                        yield PluginFunction(k, plugin['name'])
                break

class PluginFunction(object):
    """An object representing a function/command."""
    def __init__(self, function, module=None):
        self._function = function
        
        if function.__name__.startswith('re_'):
            self._type = "re"
            self.__name__ = function.__name__[3:]
        elif function.__name__.startswith('do_'):
            self._type = 'command'
            self.__name__ = function.__name__[3:]
        elif function.__name__.startswith('clock_'):
            self._type = 'clock'
            self.__name__ = function.__name__[6:]
        elif function.__name__.startswith('cmd_'):
            self._type = 'cmd'
            self.__name__ = function.__name__[4:]
        else:
            self.type = None
            self.__name__ = function.__name__
        
        self._module = module
        self._aliases = []
        if self._type == "command":
            self._aliases.append(self.__name__)
        self._re = []
        self._cmds = []
        self._private = False
        if hasattr(function, 'expr'):          # Compatibility
            self._re.append(function.expr)      # Compatibility
        if hasattr(function, 'cmd'):           # Compatibility
            self._cmds.append(function.cmd)     # Compatibility
        if hasattr(function, 'private'):       # Compatibility
            self._private = function.private   # Compatibility
    
    def aliases(self):
        for alias in self._aliases:
            yield alias
    
    def add_alias(self, alias):
        self._aliases.append(alias)
    
    def regexes(self):
        for re in self._re:
            yield re
    
    def add_regex(self, expr):
        self._re.append(expr)

    def cmds(self):
        for cmd in self._cmds:
            yield cmd
    
    def add_cmd(self, cmd):
        self._cmds.append(cmd)
    
    def add_module(self, module):
        self._module = module
    
    def module(self):
        return self._module
    
    def type(self):
        return self._type
    
    def name(self):
        return self.__name__
    
    def make_private(self, priv=True):
        self._private = priv
    
    def private(self):
        return self._private
    
    def __call__(self, *args):
        return self._function(*args)