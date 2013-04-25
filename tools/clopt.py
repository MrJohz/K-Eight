"""A very *very* simple module for dealing with command-line parsing when the
only things you need to worry about are arguments and switches."""

import re

FULL_RE = '''
(
(?:                                  ### GROUP 1
  (?:{switches})                      # will start with an options string
  (?:\w[\w_-]*)                       # followed by a word
  (?:                                 # Optional group containing:
     (?:\s*=\s*)                      #   "=" surrounded by whitespace
     (?:[\w_-]+|\".*?\"|\'.*?\')    #   word or "quoted string"
  )?                                  # Told you it was optional
  (?:\s)*                             # Followed by some whitespace
)*
)
\s+                                   # Followed by some whitespace

(                                    ### GROUP 2
  (?:
     (?:[^-].*?|\".*?\"|\'.*?\')    # A word or "quoted string"
   \s*)                               # Followed by optional whitespace
*                                     # Repeated any number of times
)
'''

OPT_RE = '''
(?:{switches})                      # will start with an options string
(\w[\w_-]*)                         # GROUP: followed by a word
(?:                                 # Optional group containing:
   (?:\s*=\s*)                      #   "=" surrounded by whitespace
   (\w[\w_-]*|\".*?\"|\'.*?\')      #   GROUP: word or "quoted string"
)?                                  # Told you it was optional
(?:\s)*                             # Followed by some whitespace
'''

ARG_RE = re.compile('''
([^-].*?|\".*?\"|\'.*?\')       # A word or "quoted string"
\s+                               # Followed by optional whitespace
''', flags=re.VERBOSE)

def clopt(args, switches=None):
    args += ' '  # to match for trailing whitespace
    switches = ['-', '--'] if switches is None else switches
    str_switches = '|'.join(switches)
    match = re.match(FULL_RE.format(switches=str_switches), args, re.VERBOSE)
    if match is None:
        return (dict(), tuple())
    
    optargs = args
    opts, args = match.groups()
    args += ' '  # ARG_RE matches for trailing whitespace.
    
    SWRE = OPT_RE.format(switches=str_switches)
    opts = {opt: arg for opt, arg in re.findall(SWRE, opts, re.VERBOSE)}
    
    args = tuple(ARG_RE.findall(args))
    return opts, args