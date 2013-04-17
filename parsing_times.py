# -*- coding: cp1252 -*-
import pprint

nums = '0123456789'
lets = 'abcdefghijklmnopqrstuvwxyz'
timestrs = ['secs', 'mins', 'hrs', 'days']
equiv_timestrs = {'secs': ['s', 'sec', 'secs', 'seconds', 'second'],
                  'mins': ['m', 'min', 'mins', 'minutes', 'minute'],
                  'hrs':  ['h', 'hr', 'hrs', 'hours', 'hour'],
                  'days': ['d', 'day', 'days']}

timestr_dic = {}
for category, items in equiv_timestrs.iteritems():
    for val in items:
        timestr_dic[val] = category

def get_type(sym):
    if sym in nums:
        return nums
    elif sym in lets:
        return lets
    else:
        return None

class InvalidCharError(Exception):
    pass

class LetNumParser(object):
    """Parsing .in strings"""
    def __init__(self, in_string):
        self.string = in_string
        self._istring = list(in_string)
        self._end = False

    def next(self):
        if self._end:
            raise StopIteration

        self._word = ''
        
        while True:
            try:
                sym = self._istring.pop(0)
            except IndexError:
                self._end = True
                return self._word

            if not sym.strip():
                continue
            else:
                self._sym_type = get_type(sym)
                if self._sym_type not in [nums, lets]:
                    continue
                self._word += sym
                break

        while True:
            try:
                sym = self._istring.pop(0)
            except IndexError:
                self._end = True
                return self._word
            
            if not sym.strip():
                continue
            elif get_type(sym) not in [nums, lets]:
                continue
            elif self._sym_type == get_type(sym):
                self._word += sym
            else:
                self._istring.insert(0, sym)
                return self._word

    def __iter__(self):
        return self

class ParseError(Exception):
    pass

def get_pairs(lnp):
    for i in lnp:
        yield i, lnp.next()

def parse(string):
    o_sym_type = lets
    retDict = {i:0 for i in timestrs}
    for i, j in get_pairs(LetNumParser(string)):
        try:
            unit = timestr_dic[i]
        except KeyError:
            continue
    
            


for i in get_pairs(LetNumParser('123s56m678"53#days566')):
    print i
