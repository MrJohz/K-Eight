## SETUP

from tools import plugin

## QUIT
@plugin.private()
def do_quit(keight, event):
    """Quits bot from server.  Can only be performed by identified admins."""
    if keight.get_account(event.source) in keight.admins:
        keight.disconnect()

## HELP
def do_help(keight, event):
    """General help documentation."""
    msg = event.message.split(' ', 1)
    try:
        command = msg[1].strip()
    except IndexError:
        if event.private:
            commands = (i for i, j in keight.commands['command'] if not j.private())
            commands = (i for i,j in keight.commands['command'])
            return ("Commands recognised: " + ', '.join(commands),
                    "Use .help <command> for more instructions.")
        else:
            msg  = "Hello.  I'm {}.  I'm a bot designed by Johz and "
            msg += "operated by {}.\n"
            msg += "For a list of commands, use .help in private."
            return msg.format(keight.nick, keight.owner)

    if not command in keight.commands:
        return "Help on command {}: That's not a command.".format(command)
    else:
        msg = "Help on command {}: {}"
        if keight.commands[command].__doc__:
            return msg.format(command, keight.commands[command].__doc__)
        else:
            return msg.format(command, "This command doesn't appear to have "
                                       "any documentation.")

# @plugin.private()
def do_reload(keight, event):
    """Reloads a module."""
    if keight.get_account(event.source) in keight.admins:
        arg = event.args
        response = keight._set_commands(arg)
        if arg and response:
            msg = 'Loaded {arg} functions from module {module}'
        elif response:
            msg = 'Loaded {arg} functions from all modules.'
        else:
            msg = 'Failed to load module.'
        return msg.format(module=arg, arg=response)


## JOIN
@plugin.private()
def do_join(keight, event):
    """Joins a channel.  Can only be performed by identified admins."""
    if keight.get_account(event.source) in keight.admins:
        message = event.message.split()
        try:
            arg = message[1].strip()
        except IndexError:
            return "I don't have anything to join."
        keight.join_channel(arg)


## PART
@plugin.private()
def do_part(keight, event):
    """Parts a channel.  Can only be performed by identified admins."""
    if keight.get_account(event.source) in keight.admins:
        message = event.message.split()
        try:
            arg = message[1].strip()
        except IndexError:
            arg = event.target
        keight.part_channel(arg)

## STATS
listify = lambda l: ', '.join(i[0] + ': ' + str(i[1]) for i in l)

def do_stats(keight, event):
    """Provides counts of the most used commands, most common users, etc"""
    commands = [i for i in keight.stats['command_count'].most_common(7)]
    commands = [i for i in commands if i[1] > 0]
    if not commands:
        return "Nobody's said anything yet!"
    lret = ["Most used commands: " + listify(commands)]
    
    users = [i for i in keight.stats['user_count'].most_common(5)]
    users = [i for i in users if i[1] > 0]
    lret.append("Most irritating users: " + listify(users))
    
    channels = [i for i in keight.stats['channel_count'].most_common(5)]
    channels = [i for i in channels if i[1] > 0]
    lret.append("Rowdiest channels: " + listify(channels))
    
    return lret

## IDENTIFIED?
def do_identified(keight, event):
    try:
        user = event.message[12:].strip().split()[0]
    except:
        return "That isn't a user, I'm afraid."
    if user:
        return "{} has identification status: {}".format(user, keight.is_identified(user))

def do_account(keight, event):
    try:
        user = event.message[8:].strip().split()[0]
    except IndexError:
        return "That isn't a user, I'm afraid."
    if user:
        return "{} is identified as: {}".format(user, keight.get_account(user))
        
