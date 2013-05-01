"""
A module to attempt to deal with the various forms of identification systems
available.  I've tried to put this list together using the biggest irc servers
that I know of, but it may well be out of date, incomplete etc.  Feel free
to add servers that you know, and their ircd ident systems.
"""

import re

RECOGNISED_SERVERS = {
    'undernet': 
        {'server_format': re.compile('^.*?\.undernet\.org$'),
         'is_identified': always_true_is_identified,
         'get_account': always_true_get_account}
    'freenode':
        {'server_format': re.compile('^.*?\.freenode\.net$'),
         'is_identified': charybdis_is_identified,
         'get_account': charybdis_get_account}
    'esper':
        {'server_format': re.compile('^.*?\.esper\.net$'),
         'is_identified': charybdis_is_identified,
         'get_account': charybdis_get_account}
    'efnet':
        {'server_format': re.compile('^\.*?\.efnet\.org$'),
         'is_identified': always_true_is_identified,
         'get_account': always_true_get_account}
    'rizon':
        {'server_format': re.compile('^\.*?\.rizon\.net$'),
         'is_identified': charybdis_is_identified,
         'get_account': charybdis_get_account}
    'quakenet':
        {'server_format': re.compile('^.*?\.quakenet.org$'),
         'is_identified': charybdis_is_identified,
         'get_account': charybdis_get_account}
    }

def always_true_is_identified(keight, user):
    return True

def always_true_get_account(keight, user):
    return user

def charybdis_is_identified(self, user):
    self.check_only(user)
    userObj = self.user_dict.get(user.lower(), None)
    if userObj is not None:
        return userObj.identified
    else:
        return None

def charybdis_get_account(self, user):
    self.check_only(user)
    userObj = self.user_dict.get(user.lower(), None)
    if userObj is not None:
        return userObj.account
    else:
        return None