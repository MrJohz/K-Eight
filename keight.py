"""
K-Eight - an extendable python IRC bot by Johz.

To run for the first time, do "{name} --new_config"

USAGE:
    {name} [--options] [#channel1 [#channel2 [...]]]

OPTIONS:
    (Required arguments for long-form options are required
    for short-form options as well.  Also note that the
    options-parsing system isn't very intelligent, so be explicit.)
    
    -h, --help            Displays this message and exits.
    --version             Displays version and exits.
    --new_config          Creates a new configuration file and exits.
    -n, --nick=NICK       Runs {name} with nick NICK. (Ignores config file)
    -s, --server=SERVER   Runs {name} with server SERVER. (Ignores config file)
    -p, --port=PORT       Runs {name} with port PORT. (Ignores config file)
    --pword=PASS          Runs {name} with password PASS. (Ignores config file)
"""

import datetime
import fnmatch
import imp
import os
import pprint
import re
import sys
import threading, Queue

from collections import Counter

from ircutils import bot, events, format
from tools import persist, config, log
from tools import plugin_imports as plugins

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

class CapCheckHandler(events.ReplyListener):
    def __init__(self):
        events.ReplyListener.__init__(self)
        self._params = ["ACK"]
    
    def notify(self, client, event):
        if event.command.upper() == "CAP":
            if event.params[0].upper() == "ACK" and event.params[1] == '*':
                self._params.extend(event.params[2:])
            elif event.params[0].upper() == "ACK":
                self._params.extend(event.params[1:])
                event.params = self._params
                self.activate_handlers(client, event)

## Helper functions and classes

blankFunc = lambda keight, event: None

def isiterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

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
    def __init__(self, config, opts=None, args=None):
        self.logger = log.Logger()
        self.commands = dict()
        for i in plugins.COMMAND_NAMES:
            self.commands[i] = dict()
        self.commands['re'] = list()
        self.commands['cmd'] = list()
        self.opts = dict() if opts is None else opts
        opts = self.opts
        self.args = tuple() if args is None else args
        args = self.args
        if 'nick' in opts:
            nick = opts['nick']
        elif 'n' in opts:
            nick = opts['n']
        else:
            nick = config.connection['nick']
        bot.SimpleBot.__init__(self, nick)
        self.nick = nick
        self.config = config
        self.owner = config.admin['owner']
        self.admins = config.admin.get('admins', [self.owner])
        if 'port' in opts:
            port = int(opts['port'][-1])
        else:
            port = config.connection['port']
        port = 6667 if port is None else port
        if 'pword' in opts:
            password = int(opts['pword'][-1])
        else:
            password = config.connection['password']
        if 'server' in opts:
            server = opts['server'][-1]
        else:
            server = config.connection['server']
        self.server, self.port, self.password = server, port, password
        self.connect(server, port=port, password=password)
        self.logger.info("Connected to {server}:{port!s} as {nick}",
                         tags=['system'], server=server, port=port, nick=nick)
        self.user_dict = {}
        self.stats = persist.PersistentDict('stats.db', writeback=True)
        self.stats['command_count'] = Counter()
        self.stats['user_count'] = Counter()
        self.stats['channel_count'] = Counter()
        self._set_commands()
        self._queue = Queue.Queue()
        self._use_ident = self.config.admin.get('use_ident', True)
        self.logger.debug("Initialised bot", tags=["system"])
        
    def start(self):
        self._timing_thread = DoTimingThread(self, self._queue)
        self._timing_thread.start()
        self.logger.debug("Started timing thread", tags=['system'])
        self.logger.debug("Starting main bot-loop", tags=['system'])
        bot.SimpleBot.start(self)
    
    def disconnect(self, message=None):
        bot.SimpleBot.disconnect(self, message)
        self.logger.info("Disconnected from server", tags=['system'])

    def _set_commands(self, module=None):
        p_folder = self.config.admin.get('plugins_folder')
        if module is None:  # Need to set *all* the commands.
            self.commands = dict()
            for i in plugins.COMMAND_NAMES:
                self.commands[i] = dict()
            self.commands['re'] = list()
        module_config = getattr(self.config, 'modules', dict())
        funcs = plugins.get_funcs(p_folder, module, module_config)
        func_no = 0
        for function in funcs:
            func_no += 1
            if function.type() == "clock":
                self.commands["clock"][function.name()] = function
                continue
            for regex in function.regexes():
                self.commands["re"].append((self._opt_compile(regex), function))
            for alias in function.aliases():
                self.commands["command"][alias] = function
            for trigger in function.cmds():
                self.commands['cmd'].append((trigger, function))
        if module is None:
            self.logger.debug("Loaded {func_no} functions from all modules.",
                              tags=['system'], func_no=func_no)
        else:
            self.logger.debug("Loaded {func_no} functions from {module}.",
                              tags=['system'], module=module, func_no=func_no)
                              
        return func_no

    def on_welcome(self, event):
        self.logger.debug("Recieved welcome message.", tags=['system'])
        chans = self.config.connection.get('channels')
        chans = list() if chans is None else chans
        chans.extend(self.args['channels'])
        for channel in chans:
            if not channel.startswith('#'):
                channel = '#' + channel
            self.join(channel)
            self.logger.info("Joined channel {channel}", tags=['system'],
                             channel=channel)
        
        try:
            ns = self.config.nickserv
        except AttributeError:
            pass
        else:
            if ns.get('command') is not None:
                command = ns['command'].split(None, 1)
                if command[0] == "MSG":
                    command[0] = "PRIVMSG"
                self.execute(*command)
            else:
                name = ns.get('name', '')
                password = ns.get('password', '')
                command = "IDENTIFY {name} {password}"
                self.send_message('NickServ',
                             command.format(name=name, password=password))
                command = "IDENTIFY {password}"
                self.send_message('NickServ',
                             command.format(password=password))
        
        # EXECUTE CAP THINGY
        self.execute("CAP", "REQ", "identify-msg")
        self.execute("CAP", "END")
    
    def on_cap_event(self, event):
        try:
            self._caps
        except:
            self._caps = {}
        if event.params[0].upper() == 'ACK':
            for param in event.params[1:]:
                if param[0] == '-':
                    self._caps[param[1:].strip()] = False
                elif param[0] == '=':
                    pass
                elif param[0] == '~':
                    pass
                else:
                    self._caps[param.strip()] = True
            
                
    def check_all(self):
        self.user_dict = {}
        for channel in self.channels:
            for user in self.channels[channel].user_list:
                self.execute('WHOIS', user)

    def check_only(self, user):
        self.execute('WHOIS', user)
        self.logger.debug("Performed 'WHOIS' on {user}",
                          tags=['system'], user=user)

    def is_identified(self, user):
        if not self._use_ident:
            return True
        self.check_only(user)
        userObj = self.user_dict.get(user.lower(), None)
        if userObj:
            return userObj.identified
        else:
            return userObj
    
    def get_account(self, user):
        if not self._use_ident:
            return True
        self.check_only(user)
        userObj = self.user_dict.get(user.lower(), None)
        if userObj:
            return userObj.account
        else:
            return None
    def _opt_compile(self, regex):
        if isinstance(regex, basestring):
            try:
                regex = regex.format(nick=self.nick)
            except KeyError:
                txt  = "Regex {regex} does not use format-safe syntax.  If it "
                txt += "does not need options-formatting, consider compiling it "
                txt += "for speed and security."
                self.logger.warning(txt, tags=['system'], regex=regex)
            return re.compile(regex)
        else:
            return regex

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
        func = self.commands['clock'].get(func_name, blankFunc)
        try:
            retVal = func(self, time, func_name, arg)
        except Exception as e:
            retVal = '{}: {}'.format(type(e).__name__, str(e))
            self.logger.error(retVal, tags=['system'])

    def do_command(self, event):
        try:
            self._caps
        except AttributeError:
            self._caps = {}
        if self._caps.get('identify-msg', False):
            id = True if event.message[0] == '+' else False
            event.message = event.message[1:]
            user_id = self.user_dict.get(event.source.lower())
            if user_id is None:
                self.check_only(event.source)
            else:
                user_id.identified = id
                if not id:
                    user_id.account = None
                    
        command_key = self.config.admin.get('command_key', '.')
        if event.private:
            target = event.source
        else:
            target = event.target
        
        if event.message.lower().startswith(self.nick.lower() + '!'):
            self.send_message(target, event.source + '!')
        
        for regex, func in self.commands['re']:
            match = regex.search(event.message)
            if match:
                event.match = match
                try:
                    retVal = func(self, event)
                except Exception as e:
                    retVal = 'Oh noes!  {}: {}'.format(type(e).__name__, str(e))
            else:
                continue
            
            if isinstance(retVal, basestring):
                self._send_linebr_message(target, str(retVal))
            elif isiterable(retVal):
                for msg in retVal:
                    if isinstance(msg, basestring):
                        self._send_linebr_message(target, str(msg))
            else:
                pass
        
        if event.message and event.message[0] == command_key:
            message = event.message.split()
            command = message[0][1:]
            args = event.message[len(command) + 1:].strip()
            event.command = command
            event.args = args
            
            secret_chans = self.config.admin.get('secret_channels', [])
            
            retFunc = self.commands['command'].get(command, blankFunc)
            conditions = (not retFunc is blankFunc,
                          target not in secret_chans)
            if all(conditions) and not retFunc.private():
                self.stats['command_count'][retFunc.name()] += 1
                self.stats['user_count'][event.source] += 1
                target_is_chan = int(target.startswith('#'))
                self.stats['channel_count'][target] += target_is_chan
                self.stats.sync()
                
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

    def on_private_message(self, event):
        event.private = True
        self.do_command(event)
                    
    def on_whois(self, event):
        self.user_dict[event.nick.lower()] = event

    def on_update_list_event(self, event):
        if event.command == "PING":
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

    def on_any(self, event):
        for cmd, func in self.commands['cmd'].items():
            if fnmatch.fnmatch(event.command, cmd):
                print vars(func)
                func(self, event)
            
if __name__ == "__main__":
    from tools import clopt
    options = ('quiet|q', 'version', 'new_config', 'nick|n=',
               'server|s=', 'port|p=', 'pword=', 'help|h')
    arguments = ('channels*',)
    try:
        opts, args = clopt.clopt(sys.argv[1:], options, arguments)
    except clopt.CloptError as exc:
        sys.exit("Error: {exc}".format(exc=exc))
    if "version" in opts:                     # version command
        print open("VERSION.txt", 'r').read()
        sys.exit(0)
    if 'new_config' in opts:
        with open('config.yml', 'w') as conf_file:
            conf_file.write(config.SAMPLE_CONFIG)
        sys.exit(0)
    if 'help' in opts:
        print __doc__.format(name=sys.argv[0]).strip()
        sys.exit(0)
    
    try:
        keight_config = config.ConfigParser(open('config.yml', 'r'))
    except IOError:
        with open('config.yml', 'w') as conf_file:
            conf_file.write(config.SAMPLE_CONFIG)
        sys.exit(0)
    except config.InvalidConfigError as err:
        print "Invalid config file: {0!s}".format(err)
        sys.exit(1)
    
    keight = Keight(keight_config, opts, args)
    keight.register_listener('whois', events.WhoisReplyListener())
    keight.register_listener('update_list_event', UpdateListsHandler())
    keight.register_listener('cap_event', CapCheckHandler())
    keight.start()
