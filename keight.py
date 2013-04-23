import re
import os
import imp
import sys
import pprint
import threading, Queue
import datetime
from collections import Counter

from ircutils import bot, events, format
from tools import persist, yaml

import keightconfig

DEF_PLUGIN_FOLDER = './plugins'

## Exceptions
class Error(Exception):
    pass

class MissingConfigError(Error, ValueError):
    pass

## Fake Logger - Ensures that logging handlers don't raise errors.
class FakeLogger(object):
    _fakeHandler = lambda *args, **kwargs: None
    debug = info = warning = error = critical = _fakeHandler

## Some custom handlers
class UpdateListsHandler(events.ReplyListener):
    def __init__(self):
        events.ReplyListener.__init__(self)

    def notify(self, client, event):
        if event.command == "MODE":
            self.activate_handlers(client, event)
        elif event.command == "PING":
            self.activate_handlers(client, event)
        elif event.command == "NICK":
            self.activate_handlers(client, event)
        elif event.command == "JOIN":
            if event.source != client.nickname:
                self.activate_handlers(client, event)
        else:
            pass

## Helper functions and classes

blankFunc = lambda keight, event: None

def opt_compile(regex):
    if isinstance(regex, basestring):
        return re.compile(regex)
    else:
        return regex

def isiterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def get_plugins():
    plugin_folder = getattr(keightconfig, 'plugin_folder', DEF_PLUGIN_FOLDER)
    plugins = []
    possiblePlugins = os.listdir(plugin_folder)
    for item in possiblePlugins:
        location = os.path.join(plugin_folder, item)
        if not os.path.isfile(location) or not location.endswith('.py'):
            continue
        name = item[:-3]
        info = imp.find_module(name, [os.path.abspath(plugin_folder)])
        plugins.append({'name':name, 'info':info})
    return plugins

def load_plugin(plugin):
    return imp.load_module(plugin['name'], *plugin['info'])

class PersistentNamespace(object):
    """A blank, persistent namespace"""
    def __init__(self, filename):
        self.filename = filename
        self.__dict__.update(persist.open(filename, 'r'))
        
    def sync(self):
        d = persist.open(self.filename)
        d.update(self.__dict__)
        d.close()

class BlankNamespace(object):
    pass

class DoTimingThread(threading.Thread):
    def __init__(self, keight, queue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._keight = keight
        self._queue = queue
        self._times = []
    
    def run(self):
        while True:
            time = self._get_from_queue()
            while time != None:
                self._times.append(time)
                time = self._get_from_queue()
            self._times = sorted(self._times)
            time_now = datetime.datetime.now()
            check_times = True
            while check_times:
                try:
                    tup = self._times.pop(0)
                except:
                    break
                if tup[0] < time_now:
                    self._send_timing_event(tup[0], tup[1:])
                else:
                    self._times.insert(0, (tup))
                    break
        
    def _send_timing_event(self, time, details):
        self._keight.do_time_event(time, details[0], details[1])
        
    def _get_from_queue(self):
        try:
            return self._queue.get(0)
        except Queue.Empty:
            return None
        
        

## The Bot
class Keight(bot.SimpleBot):
    def __init__(self):
        bot.SimpleBot.__init__(self, nick=keightconfig.nick)
        self.nick = keightconfig.nick
        self.owner = keightconfig.owner
        self.admins = getattr(keightconfig, 'admins', [keightconfig.owner])
        port = getattr(keightconfig, 'port', None)
        password = getattr(keightconfig, 'password', None)
        self.connect(keightconfig.host, port=port, password=password)
        logging.info('Joined irc server: {}'.format(keightconfig.host))
        self.user_dict = {}
        self.plugin_namespace = BlankNamespace()
        self.plugin_namespace.persist = PersistentNamespace('keight.db')
        self.commands = {}
        self.clock_commands = {}
        self.re_commands = []
        self.command_count = Counter({i:0 for i in self.commands})
        self.user_count = Counter()
        self.channel_count = Counter()
        self._set_commands()
        self._queue = Queue.Queue()
        
    def start(self):
        self._timing_thread = DoTimingThread(self, self._queue)
        self._timing_thread.start()
        bot.SimpleBot.start(self)
    
    def disconnect(self, message=None):
        self.plugin_namespace.persist.sync()
        bot.SimpleBot.disconnect(self, message)

    def _set_commands(self, module=None):
        if not module:
            self.commands = {}
            self.clock_commands = {}
            self.re_commands = []
            for i in get_plugins():
                try:
                    plugin = load_plugin(i)
                    for j, k in vars(plugin).items():
                        if callable(k) and j[:3] == 'do_':
                            self.commands[j[3:]] = k
                        elif callable(k) and j[:6] == 'clock_':
                            self.clock_commands[j] = k
                        elif callable(k) and j[:3] == 're_':
                            self.re_commands.append((opt_compile(k.expr), k))
                    logging.info("Loaded {}".format(i['name']))
                except ImportError as exc:
                    text = "Failed to load module {}".format(i['name'])
                    text += ": {}".format(exc)
                    logging.warning(text)
            return True
        else:
            for i in get_plugins():
                if i['name'] == module:
                    try:
                        plugin = load_plugin(i)
                        for j, k in vars(plugin).items():
                            if callable(k) and j[:3]:
                                self.commands[j[3:]] = k
                            elif callable(k) and j[:6] == 'clock_':
                                self.clock_commands[j] = k
                            elif callable(k) and j[:3] == 're_':
                                self.re_commands.append((opt_compile(k.expr), k))
                        logging.info("Loaded {}".format(i['name']))
                        return module
                    except ImportError as exc:
                        text = "Failed to load module {}".format(i['name'])
                        text += ": {}".format(exc)
                        logging.warning(text)
                        return None
            text = "Failed to load module {}".format(module)
            text += ": Module does not exist."
            logging.warning(text)
            return None

    def check_all(self):
        logging.debug('Checking all users')
        self.user_dict = {}
        for channel in self.channels:
            for user in self.channels[channel].user_list:
                self.execute('WHOIS', user)

    def check_only(self, user):
        logging.debug('Checking user {}'.format(user))
        self.execute('WHOIS', user)

    def is_identified(self, user):
        self.check_only(user)
        userObj = self.user_dict.get(user.lower(), None)
        if userObj:
            return userObj.identified
        else:
            return userObj
    
    def get_account(self, user):
        self.check_only(user)
        userObj = self.user_dict.get(user.lower(), None)
        if userObj:
            return userObj.account
        else:
            return None

    def on_welcome(self, event):
        if isinstance(keightconfig.channels, list):
            for channel in keightconfig.channels:
                self.join(channel)
                logging.debug('Joined channel {}'.format(channel))
        elif isinstance(keightconfig.channels, basestring):
            self.join(keightconfig.channels)
            logging.debug('Joined channel {}'.format(keightconfig.channels))

    def _send_linebr_message(self, target, message):
        message = message.split('\n')
        for line in message:
            self.send_message(target, line)
        
    def add_time_event(self, time, func_name, arg=None):
        if not isinstance(time, datetime.datetime):
            txt  = "'time' value must be of type datetime.datetime, recieved"
            txt += "value of type {}".format(type(time))
            raise TypeError(txt)
        
        self._queue.put((time, func_name, arg), False)
    
    def do_time_event(self, time, func_name, arg):
        func = self.clock_commands.get(func_name, blankFunc)
        try:
            retVal = func(self, time, func_name, arg)
        except Exception as e:
            retVal = '{}: {}'.format(type(e).__name__, str(e))
            print retVal

    def do_command(self, event):
        if event.private:
            target = event.source
        else:
            target = event.target
        
        if event.message.lower().startswith(self.nick.lower() + '!'):
            self.send_message(target, event.source + '!')
        
        for regex, func in self.re_commands:
            if regex.match(event.message):
                try:
                    retVal = func(self, event)
                except Exception as e:
                    retVal = 'Oh noes!  {}: {}'.format(type(e).__name__, str(e))
            
            if isinstance(retVal, basestring):
                self._send_linebr_message(target, str(retVal))
            elif isiterable(retVal):
                for msg in retVal:
                    if isinstance(msg, basestring):
                        self._send_linebr_message(target, str(msg))
            else:
                pass
        
        if event.message and event.message[0] == keightconfig.command_key:
            message = event.message.split()
            command = message[0][1:]
            args = event.message[len(command) + 1:].strip()
            event.command = command
            event.args = args
            
            retFunc = self.commands.get(command, blankFunc)
            conditions = (not retFunc is blankFunc,
                          target not in getattr(keightconfig, 'secretchannels', []),
                          not getattr(retFunc, 'private', False))
            if all(conditions):
                self.command_count[command] += 1
                self.user_count[event.source] += 1
                self.channel_count[target] += 1 if target.startswith('#') else 0
                
            try:
                retVal = retFunc(self, event)
            except Exception as e:
                retVal = 'Oh noes!  {}: {}'.format(type(e).__name__, str(e))
            if isinstance(retVal, basestring):
                retVal = str(retVal)
                self._send_linebr_message(target, retVal)
            elif isiterable(retVal):
                for msg in retVal:
                    if isinstance(msg, basestring):
                        self._send_linebr_message(target, msg)
            else:
                return


    def on_channel_message(self, event):
        event.private = False
        self.do_command(event)
        #self.command_threads.append(DoCommandThread(self, event))
        #self.command_threads[-1].start()
                    
    def on_whois(self, event):
        self.user_dict[event.nick.lower()] = event

    def on_update_list_event(self, event):
        if event.command == "PING":
            self.plugin_namespace.persist.sync()
            self.check_all()
        elif event.command == "MODE":
            if event.target in self.channels:
                # Someone's changed the mode of the channel.
                pass
            else:
                self.check_only(event.source)
        elif event.command == "QUIT":
            self.user_dict[event.source.lower()] = None
        elif event.command == "PART":
            self.check_all()
        elif event.command == "NICK":
            self.check_only(event.target)
        else:
            self.check_only(event.source)

    def on_private_message(self, event):
        event.private = True
        self.do_command(event)
        #self.command_threads.append(DoCommandThread(self, event))
        #self.command_threads[-1].start()

    def on_any(self, event):
        #pprint.pprint(vars(event))   # debugging line
        # TODO: Add event command handler thingymagig.  It'll be cool.
        pass
            
if __name__ == "__main__":
    for param in ['nick', 'host', 'channels', 'owner']:
        if not getattr(keightconfig, param, None):
            raise MissingConfigError('Parameter %s not in config. '
                                     'Please check installation '
                                     'instructions to ensure your '
                                     'config file is correct.' % param)

    if not hasattr(keightconfig, 'command_key'):
        keightconfig.command_key = '.'

    if getattr(keightconfig, 'logging', True):
        import logging
        loggingConf = {}
        for i in ['filename', 'format', 'filemode',
                  'datefmt', 'stream']:
            if hasattr(keightconfig, i):
                loggingConf[i] = getattr(keightconfig, i)
        loglevel = getattr(keightconfig, 'level', 'info')
        loggingConf['level'] = getattr(logging, loglevel.upper(), logging.INFO)
        logging.basicConfig(**loggingConf)
    else:
        logging = FakeLogger()
        
    keight = Keight()
    keight.register_listener('whois', events.WhoisReplyListener())
    keight.register_listener('update_list_event', UpdateListsHandler())
    keight.start()
