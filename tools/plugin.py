import re

from plugin_imports import PluginFunction

def action(string):
    """Turns a string into an ACTION string (by adding ACTION magic to it)"""
    return chr(1) + "ACTION " + string + chr(1)

def alias(*names):
    def decorator(function):
        function = PluginFunction(function)
        for name in names:
            function.add_alias(name)
        return function
    return decorator

def add_regex(*regexes):
    def decorator(function):
        function = PluginFunction(function)
        for regex in regexes:
            function.add_regex(regex)
        return function
    return decorator

def compile_regex(regex, flags):
    def decorator(function):
        function = PluginFunction(function)
        regex2 = re.compile(regex, flags)
        function.add_regex(regex2)
        return function
    return decorator

def add_cmd(*cmds):
    def decorator(function):
        function = PluginFunction(function)
        for cmd in cmds:
            function.add_cmd(cmd)
        return function
    return decorator

def private(priv=True):
    def decorator(function):
        function = PluginFunction(function)
        function.make_private(priv)
        return function
    return decorator