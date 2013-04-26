import imp
import os

from log import Logger

DEF_PLUGIN_FOLDER = './plugins'

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

def get_funcs(plugin_folder=DEF_PLUGIN_FOLDER, name=None):
    if name is None:
        for plugin in get_plugins(plugin_folder):
            plug = load_plugin(plugin)
            if plug is None:
                continue
            for j, k in vars(plug).items():
                if callable(k):
                    yield j, k
    else:
        for plugin in get_plugins(plugin_folder):
            if plugin['name'] == name:
                plug = load_plugin(plugin)
                if plug is None:
                    break
                for j, k in vars(plug).items():
                    if callable(k):
                        yield j, k
                break