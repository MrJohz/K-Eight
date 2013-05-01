from fnmatch import fnmatch
import datetime
import os

from tools import plugin

def dir_open(file_name, mode='a', buffering=-1):
    k_dir = os.path.split(os.path.dirname(__file__))[0]
    p_dir = os.path.join(k_dir, 'logs')
    file_name = os.path.abspath(os.path.join(p_dir, file_name))
    if not os.path.isdir(os.path.split(file_name)[0]):
        os.makedirs(os.path.split(file_name)[0])
    return open(file_name, mode, buffering)

@plugin.add_cmd("*")
def cmd_anything(keight, event):
    functions = [LOG_TRIGGERS[j] for j in LOG_TRIGGERS if fnmatch(event.command, j)]
    for f in functions:
        msg = f(keight, event)
        if msg is not None:
            f_name = "channel_logs\{server}\{date}\{channel_name}"
            server = keight.server
            date = datetime.datetime.now().strftime("%d-%m-%Y")
            channel_name = event.target if event.target.startswith('#') else event.source
            file = dir_open(f_name.format(date=date,
                                          channel_name=channel_name,
                                          server=server))
            file.write(msg)
            file.write('\n')
            file.flush()
            file.close()

def _JOIN(keight, event):
    return " * {source} has joined {target}".format(source=event.source, target=event.target)

def _PART(keight, event):
    return " * {source} has left {target}".format(source=event.source, target=event.target)

def _PRIVMSG(keight, event):
    return " <{source}> {message}".format(source=event.source, message=event.message)

def _ACTION(keight, event):
    return " ** {source} {message}".format(source=event.source, message=' '.join(event.params))

def _QUIT(keight, event):
    try:
        quit_message = event.params[0]
    except IndexError:
        quit_message = ''
    return " * {source} has quit ({quit_message})".format(source=event.source, quit_message=quit_message)

def _MODE(keight, event):
    try:
        mode, nick = event.params
    except:
        return None
    return " * {user} has given {nick} mode {mode}".format(user=event.user,
                                                           nick=nick,
                                                           mode=mode)

def _NOTICE(keight, event):
    return " -{user}- {message}".format(user=event.source, message=event.message)

LOG_TRIGGERS = {'JOIN': _JOIN,
                'PART': _PART,
                'PRIVMSG': _PRIVMSG,
                'CTCP_ACTION': _ACTION,
                'QUIT': _QUIT,
                'MODE': _MODE,
                'NOTICE': _NOTICE}
