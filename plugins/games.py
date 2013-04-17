## SETUP

import random

## ROLL (.roll)

def do_roll(keight, event):
    """Rolls dice.
USAGE: .roll
==> Rolls one six-sided dice
USAGE: .roll [<m>=1]d<n>
==> Rolls <m> <n>-sided dice (dnd notation)"""
    msg = event.message[5:].strip().lower()
    if not msg:
        return "{}: You rolled {}".format(event.source, random.randint(1,6))
    elif not 'd' in msg:
        ret = "{}: That wasn't a D&D roll.  Try .roll 1d6 for a normal dice."
        return ret.format(event.source)
    parts = [i for i in msg.split('d') if i.strip()]
    if len(parts) == 1:
        noDice = 1
    elif len(parts) == 2:
        try:
            noDice = int(parts[0])
        except IndexError:
            ret = "{}: That wasn't a D&D roll.  Try .roll or .roll 1d6 for a normal dice."
            return ret.format(event.source)
    else:
        ret = "{}: That wasn't a D&D roll.  Try .roll or .roll 1d6 for a normal dice."
        return ret.format(event.source)

    try:
        noNumbers = int(parts[-1])
    except:
        ret = "{}: That wasn't a D&D roll.  Try .roll or .roll 1d6 for a normal dice."
        return ret.format(event.source)
    
    if noDice > 99 or noNumbers > 99:
        ret = "{}: Don't you come in here trying to confuse me with your big numbers..."
        return ret.format(event.source)
    

    rolls = []
    for i in xrange(noDice):
        rolls.append(random.randint(1,noNumbers))

    if 1 < len(rolls) <= 9:
        strRolls = ' + '.join(str(i) for i in rolls)
        ret = "{}: You rolled {} (rolls: {})"
        return ret.format(event.source, sum(rolls), strRolls)

    else:
        return "{}: You rolled {}".format(event.source, sum(rolls))

def do_decide(keight, event):
    msg = event.message[8:].strip()
    if '|' in msg:
        msg = [i.strip() for i in msg.split('|')]
        if not all(msg):
            ret = "I'm sorry {}, but some of those options don't exist."
            ret = ret.format(event.source)
        else:
            ret = '{}: {}'.format(event.source, random.choice(msg))
    else:
        ret = "I'm sorry {}, but you haven't given me anything to choose from there."
        ret = ret.format(event.source)
    return ret

do_choice = do_decide

#def do_rr(keight, event):
#    return ("You know what?  Shut up.  Stop with your damn spamming, and just shut up.")



# TODO: Bingo?  CaH.