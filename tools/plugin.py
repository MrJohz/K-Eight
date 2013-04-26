def action(string):
    """Turns a string into an ACTION string (by adding ACTION magic to it)"""
    return chr(1) + "ACTION " + string + chr(1)

##TODO: Alias function.