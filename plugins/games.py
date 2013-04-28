## SETUP

import random
from operator import add, sub
import re

from tools import plugin

## ROLL (.roll)

DICE_REGEX = re.compile('^(\d+)?\s*d\s*(\d+)(?:\s*(\+|-)\s*(\d+))?$')

def do_roll(keight, event):
    """Rolls dice.
USAGE: .roll
==> Rolls one six-sided dice
USAGE: .roll [<m>=1]d<n>
==> Rolls <m> <n>-sided dice (dnd notation)"""
    msg = event.args.lower()
    if not msg:
        return "{}: You rolled {}".format(event.source, random.randint(1,6))
    match = DICE_REGEX.match(msg.strip())
    if match is not None:
        dice_no, sides, op, mod = match.groups()      # Un-group the match
        sides = int(sides)
        dice_no = 1 if dice_no is None else int(dice_no)  # Set optional params
        mod = 0 if mod is None else int(mod)              # to default vals
        op = add if op == '+' else sub
        
        if dice_no > 1000: # You cannot be serious.
            return ("There are way too many dice there for me to keep "
                    "track of.  What do you think I am, a robot?")
        
        roll_list = []
        for i in range(dice_no):
            roll_list.append(random.randint(1,sides))
        
        total = op(sum(roll_list), mod)
        roll_list = map(str, roll_list)
        ret = "{}: You rolled {}".format(event.source, total)
        if 1 < dice_no < 15:
            ret += " (rolls: {})".format(' + '.join(roll_list))
        return ret
    else:
        ret = "{}: I didn't understand any of that.  Come again?"
        return ret.format(event.source)

@plugin.alias('choice')
def do_decide(keight, event):
    """Makes hard decisions easy.
USAGE: .decide <option 1>|<option 2>|<option 3>|etc."""
    msg = event.message[8:].strip()
    if '|' in msg:
        msg = [i.strip() for i in msg.split('|')]
        if not all(msg):
            ret = "I'm sorry {}, but some of those options don't exist."
            ret = ret.format(event.source)
        else:
            ret = '{}: {}'.format(event.source, random.choice(msg))
    else:
        ret  = "I'm sorry {}, but you haven't given me anything to choose"
        ret += "from there."
        ret = ret.format(event.source)
    return ret

def do_rr(keight, event):
    return ("You know what?  Shut up.  Stop with your damn spamming, and "
            "just shut up.")

BOO_CHOICES = ('Aaaaargh!', "Wait, what was that?", 'What the *hell*?',
               "I'm scared!", plugin.action("jumps"))

@plugin.compile_regex("(?:\s|^|[{([])boo(?:[])}!. ]|$)", re.IGNORECASE)
def do_boo(keight, event):
    return random.choice(BOO_CHOICES)