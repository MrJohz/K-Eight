import re

from tools import persist

{'kick {user} from {channel}': '.kick {user} {channel}',
 'please kick {user} from {channel}': '.kick {user} {channel}',
 'get rid of {user}': '.kick {user}',
 '{string} means {string}': '.add_equiv "{string}" "{string}"',
 '{string} means do {command}': '.add_command "{string}" "{command}"'}

TYPES = {'user': r'(?P<user>[][A-Za-z_|\^{}-][][A-Za-z0-9_\^{}-|]+)',
         'channel': r'(?P<channel>[#&+][^, :]+|!![A-Z0-9]{5})'
         'string': r'(?P<quote>["\'])(?P<string>.*)(?P=quote)'
         'command': '(?P<quote>["\'])(?P<command>\..*)(?P=quote)'}

COMMANDS = persist.PersistentDict('natural.db', writeback=True)

def re_natural(keight, event):
    for expr, command in COMMANDS.items():
        expr = expr.format(**TYPES)
        match = re.search(expr, event.match.group(1))
        if match is None:
            continue
        

re_natural.expr = "{keight.nick}[!,]?\s(.*?)"


RE_ADD_EQUIV = re.compile('(?P<quote>["\'])(?P<string1>.*)(?P=quote)'
                          '\s+
                          '(?P<quote>["\'])(?P<string2>.*)(?P=quote)')
def do_add_equiv(keight, event):
    match = RE_ADD_EQUIV.search(event.args)
    if match is None:
        return "Did you get the syntax right there?"
    string1, string2 = match.groupdict['string1'], match.groupdict['string2']