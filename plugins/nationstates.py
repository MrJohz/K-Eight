from __future__ import division
import datetime

from tools.web import urllib
from tools import persist

from tools.nstoolkit.approximation import approx, next, prev

lengths = persist.PersistentDict('ns_update_lengths.db')
majorlength = lengths.get("major_length")
minorlength = lengths.get("minor_length")

## Nation

def do_nation(keight, event):
    """Links to a NationStates nation.
USAGE: .n[ation] <nation name>
-->  http://www.nationstates.net/nation=<nation_name>"""
    message = event.args
    if not message:
        return "{}: Usage is .n <nation name>".format(event.source)

    nation = message.strip().replace(' ', '_').lower()
    user = event.source
    return '{}: http://www.nationstates.net/nation={}'.format(user, nation)

do_n = do_nation
## Region

def do_region(keight, event):
    """Links to a NationStates region.
USAGE: .r[egion] <region name>
-->  http://www.nationstates.net/region=<region_name>"""
    message = event.args.strip()
    if not message:
        return "{}: Thats not a region.  That's not even a thing.".format(event.source)
        
    region = message.strip().replace(' ', '_').lower()
    user = event.source
    return '{}: http://www.nationstates.net/region={}'.format(user, region)

do_r = do_region

def do_dossier(keight, event):
    """Dossier's a NationStates region."""
    message = event.args
    if not message:
        return "{}: That doesn't work, try again.".format(event.source)
    
    nation = message.strip().replace(' ', '_').lower()
    ret = "{}: http://www.nationstates.net/page=dossier?nation={}&action=add"
    return ret.format(event.source, nation)

do_d = do_dossier

def do_boneyard(keight, event):
    """Links to the NationStates boneyard page for a nation."""
    message = event.args
    if not message:
        return "{}: Wut?  There wasn't a nation name there.".format(event.source)
    
    nation = message.strip().replace(' ', '_').lower()
    ret = "{}: http://www.nationstates.net/page=boneyard/nation={}"
    return ret.format(event.source, nation)

do_b = do_boneyard
    
## approx

def do_approx(keight, event):
    region = event.message[7:].strip()
    targ = event.source if event.private else event.target
    if not event.target == '#udl-cmd':
      pass
        #keight.send_message('#udl-cmd', "{} is using approx on {} in {}".format(event.source, region, targ))
    if majorlength is not None:
        update_time = approx(region, False, majorlength)
        if update_time == -1:
            return "I think NS is down, but don't quote me on that."
        elif update_time:
            return "{}: {}".format(event.source, update_time)
        else:
            mes = "{}: I think {} is just a figment of your imagination."
            return mes.format(event.source, region)
    else:
        return '{}: major_length has not been set yet.'.format(event.source)



## minor

def do_minor(keight, event):
    region = event.args.strip()
    targ = event.source if event.private else event.target
    if not event.target == '#udl-cmd':
        keight.send_message('#udl-cmd', "{} is using minor on {} in {}".format(event.source, region, targ))
    if minorlength is not None:
        update_time = approx(region, False, minorlength)
        if update_time == -1:
            return "I think NS is down, but don't quote me on that."
        elif update_time:
            return "{}: {}".format(event.source, update_time)
        else:
            mes = "{}: I think {} is just a figment of your imagination."
            return mes.format(event.source, region)
    else:
        m = "{}: I'm waiting for someone to tell me how long minor update lasts.  :("
        return m.format(event.source)

## set_minor/major_length

def do_setminor(keight, event):
    global minorlength, lengths
    if not event.source in keight.admins and keight.is_identified(event.source):
        return
    secs_length = event.args.strip()
    try:
        secs = int(secs_length)
    except ValueError:
        return "{}: That's not a number.".format(event.source)
    lengths["minor_length"] = secs
    minorlength = secs
    return "Minor length set to {}".format(secs)
    
def do_setmajor(keight, event):
    global majorlength, lengths
    if not event.source in keight.admins and keight.is_identified(event.source):
        return
    secs_length = event.args.strip()
    try:
        secs = int(secs_length)
    except ValueError:
        return "{}: That's not a number.".format(event.source)
    lengths["major_length"] = secs
    majorlength = secs
    return "Major length set to {}".format(secs)
    
## next, prev

def do_next(keight, event):
    region = event.args.strip()
    next_region = next(region)
    if next_region == -1:
        return "OH NOES!  NS IS DOWN!  ABANDON SHIP!"
    elif next_region:
        return "{}: {}".format(event.source, next_region)
    else:
        return "{}: Could not find region.".format(event.source)

def do_prev(keight, event):
    region = args.strip()
    prev_region = prev(region)
    if prev_region == -1:
        return "OH NOES!  NS IS DOWN!  ABANDON SHIP!"
    elif prev_region:
        return "{}: {}".format(event.source, prev_region)
    else:
        return "{}: Could not find region.".format(event.source)


## Endo-Count tools
# TODO: Complete this bit

#def do_ec(keight, event):
#    nation = event.message[4].strip()
    
    

## Fun and games

def do_doable(keight, event):
    return "Hey, that seems... http://www.nationstates.net/region=doable"
'''
import datetime

def do_permaregload(keight, event):
    if not event.source in keight.admins and keight.is_identified(event.source):
        return
    today = datetime.date.today()
'''
