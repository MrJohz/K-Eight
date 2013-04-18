## Connection Settings
nick = "K-Eight"
host = 'irc.esper.net'
port = 6667
# password = 
channels = ['#johztestingchannel']
owner = 'Johz'

## Admin Settings
admins = [owner, 'Solm']

## Logging Settings
logging = True
level = 'info'

# This is the character that defines a command (the . in .tell, for example)
# It will default to '.' if no key is chosen.
# command_key = '.'

plugins_folder = './plugins'


## Stuff below here isn't actually working.  At all.

# Default modules
exclude = ['badmodule', 'verybadmodule']

# Block modules from specific channels
# To not block anything for a channel, just don't mention it
excludes = {'#badchannel':['module1', 'module2'],
            '#otherchannel':['onebadmodule']}

# Allow modules in specific channels
# This overides exclude.
enables = {'#goodchannel':'secretmodule'}

