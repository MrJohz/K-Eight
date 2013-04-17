from __future__ import division

import re
import datetime
from tools import persist

TIMESTRS = ['secs', 'mins', 'hrs', 'days']
TIMESTR_TIMES = dict(zip(TIMESTRS, [1, 60, 60*60, 24*60*60]))

# I think this is a more elegant way of creating a dictionary
# of 'abbreviation': 'meaning' pairs, but who knows?
EQUIV_TIMESTRS = {'secs': ['s', 'sec', 'secs', 'seconds', 'second'],
                  'mins': ['m', 'min', 'mins', 'minutes', 'minute'],
                  'hrs':  ['h', 'hr', 'hrs', 'hours', 'hour'],
                  'days': ['d', 'day', 'days']}
TIMESTR_DICT = dict()
for category, items in EQUIV_TIMESTRS.iteritems():
    for val in items:
        TIMESTR_DICT[val] = category

ACCEPT = sorted(TIMESTR_DICT, key=len, reverse=True) # Ensures Regex matches
                                                     # in the correct order.
                                                     
SPLITSTRING = r'((?:\d+\s*(?:{})\s*)+)\s*(.*)'
RE_SPLITSTRING = re.compile(SPLITSTRING.format('|'.join(ACCEPT)))
RE_GETTIMES = re.compile(r'(\d+)\s*({})\s*'.format('|'.join(ACCEPT)))

def get_messages(string):
    # TODO: support decimal/float time periods (eg: 3.5secs, 4.2 minutes)
    try:
        times, messages = RE_SPLITSTRING.search(string).groups()
    except AttributeError:
        return None
    times = [(i, TIMESTR_DICT[j]) for i,j in RE_GETTIMES.findall(times)]
    return times, messages

def prettify_time(t):
    ss = int(round(t.total_seconds()))
    mm, ss = divmod(ss, 60)
    hh, mm = divmod(mm, 60)
    dd, hh = divmod(hh, 24)
    
    ss = int(ss)
    mm = int(mm)
    hh = int(hh)
    dd = int(dd)
    
    parts = []
    
    if ss:
        msg = "{ss} seconds" if ss > 1 else "{ss} second"
        parts.append(msg)
    if mm:
        msg = "{mm} minutes" if mm > 1 else "{mm} minute"
        parts.append(msg)
    if hh:
        msg = "{hh} hours" if hh > 1 else "{hh} hour"
        parts.append(msg)
    if dd:
        msg = "{dd} days" if dd > 1 else "{dd} day"
        parts.append(msg)
    
    # The Oxford Comma joining algorithm below is a slightly reduced
    # version of Kenneth Reitz' clint.eng.join algorithm.
    # (https://github.com/kennethreitz/clint/blob/develop/clint/eng.py)
    pos = len(parts)
    new_parts = []
    for part in parts[::-1]:
        pos -= 1
        new_parts.append(part)
        if pos == 1:
            if len(parts) == 2:
                new_parts.append(' ')
            else:
                new_parts.append(', ')
            new_parts.append('and ')
        elif pos is not 0:
            new_parts.append(', ')
    return ''.join(new_parts).format(**locals()) # dangerous, but probably okay.

## in

def do_in(keight, event):
    try: # Let's try and get the time and message out with regex.
        times, message = get_messages(event.message[4:].strip())
    except TypeError:
        try: # Maybe the input was just a number?
            secs = float(event.message[4:].strip())
        except ValueError: # Give up and shut up.
            response = "{}: I'm afraid that didn't make much sense to me."
            return response.format(event.source) + " Try again?"
        else:
            event.alert_message = ''
    else:
        secs = sum(TIMESTR_TIMES[j] * int(i) for i,j in times)
        event.alert_message = message
    
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=secs)
    then = now + delta
    keight.add_time_event(then, 'clock_alert', event)
    return "I'll remind you about that in {}.".format(prettify_time(delta))
    

def clock_alert(keight, time, func_name, arg):
    msg = arg.alert_message
    if msg.strip() is not '':
        line = "{}: {}".format(arg.source, msg)
    else:
        line = "{}!".format(arg.source)
    keight.send_message(arg.target, line)
    
## tell/note

def do_tell(keight, event):
    msg = event.message[6:].strip()
    try:
        sendee, message = msg.split(' ', 1)
    except ValueError:
        return "There's no message there."
    
    if sendee[-1] != '*':
        try:
            d = keight.plugin_namespace.messages.get(sendee.lower(), [])
            d.append((event.source, message, datetime.datetime.now()))
            keight.plugin_namespace.messages[sendee.lower()] = d
        except AttributeError: # Clearly messages hasn't been defined yet.
            keight.plugin_namespace.messages = persist.open('messages.db')
            d = keight.plugin_namespace.messages.get(sendee.lower(), [])
            d.append((event.source, message, datetime.datetime.now()))
            keight.plugin_namespace.messages[sendee.lower()] = d
    else:
        try:
            d = keight.plugin_namespace.star_messages.get(sendee.lower(), [])
            d.append((event.source, message, datetime.datetime.now()))
            keight.plugin_namespace.star_messages[sendee.lower()] = d
        except AttributeError:
            keight.plugin_namespace.star_messages = persist.open('star_messages.db')
            d = keight.plugin_namespace.star_messages.get(sendee.lower(), [])
            d.append((event.source, message, datetime.datetime.now()))
            keight.plugin_namespace.star_messages[sendee.lower()] = d
    
    keight.plugin_namespace.messages.sync()
    return '{}: I\'ll tell {} "{}" when I next see them.'.format(event.source, sendee, message)

def re_any(keight, event):
    retMes = []
    try:
        messages = keight.plugin_namespace.messages.get(event.source.lower().strip(), [])
        keight.plugin_namespace.messages[event.source.lower()] = []
        del keight.plugin_namespace.messages[event.source.lower().strip()]
    except AttributeError:
        return
    if messages:
        now = datetime.datetime.now()
        for sender, mess, time in messages:
            diff = now - time
            timestr = prettify_time(diff) + ' ago'
            m = "{}: {} left you this message {}. \"{}\""
            m = m.format(event.source, sender, timestr, mess)
            retMes.append(m)
    
    messages = []
    try:
        for i, j in keight.plugin_namespace.star_messages.items():
            if event.source.startswith(i[:-1]):
                messages.extend(j)
    except AttributeError:
        return
    if messages:
        for sender, mess, time in messages:
            diff = now - time
            timestr = prettify_time(diff) + 'ago'
            m = "{}: {} left you this message {}. \"{}\""
            m = m.format(event.source, sender, timestr, mess)
            retMes.append(m)
            
    if retMes:
        return retMes

re_any.expr = '.*'
