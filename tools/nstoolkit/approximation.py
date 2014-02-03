from __future__ import division
from collections import OrderedDict
import dumphandler

def get_simple_name(name):
    return name.strip().replace(' ', '_').lower()

dump = dumphandler.ApiHandler('Update Time Approximation | Johz').getDump()
numDict = OrderedDict()
totNats = 0
for name, size in dump.iterAttr('NUMNATIONS'):
    numDict[get_simple_name(name)] = totNats
    totNats += int(size)

def approx(region, minor=True, length=4620, start=0):
    "Minor length: 4620 (ish)"
    region = get_simple_name(region)
    if not region in numDict:
        return None

    length = length - start
    natTime = length / totNats
    sumTime = numDict[region] * natTime

    sumTime = round(sumTime + start)
    secs = sumTime % 60
    mins = sumTime // 60
    hrs = (mins // 60) + 12 if minor else (mins // 60)
    mins = mins % 60
    time = '%(hrs)02d:%(mins)02d:%(secs)02d' % {'secs':round(secs),
                                                'mins':mins,
                                                'hrs':hrs}
    return time

def extrapolate(region, hrs, mins, secs, minor=False):
    totNo = 0
    for reg, no in numDict.iteritems():
        if not get_simple_name(reg) == get_simple_name(region):
            totNo += int(no)
        else:
            break
    if minor:
        hrs -= 12
    time = (((hrs * 60) + mins) * 60) + secs
    natTime = time / totNo
    return natTime * totNats

def next(region):
    try:
        return numDict.keys()[numDict.keys().index(region) + 1]
    except ValueError:
        return None
    except IndexError:
        return "{} is the last region in update.".format(region)

def prev(region):
    try:
        return numDict.keys()[numDict.keys().index(region) - 1]
    except ValueError:
        return None
    except IndexError:
        return "{} is the first region in update.".format(region)
