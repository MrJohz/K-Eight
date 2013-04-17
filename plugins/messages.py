from __future__ import division

import re
import datetime
#from tools import persist

TIMESTRS = ['secs', 'mins', 'hrs', 'days']
TIMESTR_TIMES = dict(zip(TIMESTRS, [1, 60, 60*60, 24*60*60]))
EQUIV_TIMESTRS = {'secs': ['s', 'sec', 'secs', 'seconds', 'second'],
                  'mins': ['m', 'min', 'mins', 'minutes', 'minute'],
                  'hrs':  ['h', 'hr', 'hrs', 'hours', 'hour'],
                  'days': ['d', 'day', 'days']}

TIMESTR_DICT = {}
for category, items in EQUIV_TIMESTRS.iteritems():
    for val in items:
        TIMESTR_DICT[val] = category

ACCEPT = sorted(TIMESTR_DICT, key=len, reverse=True)

SPLITSTRING = r'((?:\d+\s*(?:{})\s*)+)\s*(.*)'
RE_SPLITSTRING = re.compile(SPLITSTRING.format('|'.join(ACCEPT)))
RE_GETTIMES = re.compile(r'(\d+)\s*({})\s*'.format('|'.join(ACCEPT)))

def get_messages(string):
    try:
        times, messages = RE_SPLITSTRING.search(string).groups()
    except AttributeError:
        return None
    times = [(i, TIMESTR_DICT[j]) for i,j in RE_GETTIMES.findall(times)]
    return times, messages

def prettify_time(t):
    ss = t.total_seconds()
    mm, ss = ss / 60, ss % 60
    hh, mm = mm / 60, mm % 60
    dd, hh = hh / 60, hh % 60
    
    ss = int(ss)
    mm = int(mm)
    hh = int(hh)
    dd = int(dd)
    if dd == 0 and hh == 0 and mm == 0:
        return "{} second(s)".format(ss)
    elif dd == 0 and hh == 0:
        return "{} minute(s) and {} second(s)".format(mm, ss)
    elif dd == 0:
        return "{} hour(s), {} minute(s) and {} second(s)".format(hh, mm, ss)
    else:
        return "{} day(s), {} minute(s) and {} second(s)".format(dd, hh, mm, ss)

## in

def do_in(keight, event):
    try:
        times, message = get_messages(event.message[4:].strip())
    except TypeError:
        response = "{}: I'm afraid that didn't make much sense to me."
        return response.format(event.source) + " Try again?"

    secs = sum(TIMESTR_TIMES[j] * int(i) for i,j in times)
    print secs
    event.alert_message = message
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=secs)
    then = now + delta
    keight.add_time_event(then, 'clock_alert', event)
    return "Will remind in {} seconds".format(secs)
    

def clock_alert(keight, time, func_name, arg):
    msg = arg.alert_message
    line = "{}: {}".format(arg.source, msg)
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
