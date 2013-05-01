---
layout: default
---

> K-Eight is fast, easy to extend, friendly, and designed for everything from chatting to channel management.
> Have fun.

## What is K-Eight?
K-Eight is a Python IRC bot designed by [myself][johz] using Evan Fosmark's [IRCUtils][ircutils] to deal with the IRC abstractions.  It is currently in the process of being padded out with extra features such as IRC logging and the whole host of commands and triggers that one expects from a fully-featured IRC bot.  However it is already a powerful tool, with its own internal logging system and a powerful toolkit.

[johz]: <http://johz.wordpress.com>
[ircutils]: <http://dev.guardedcode.com/projects/ircutils/>

K-Eight is designed around the principle of plugins.  Plugins can be included and excluded easily from a single YAML configuration file, but they can also be modified and added to by anyone who understands how to write a function in Python.  K-Eight will automatically recognise plugin scripts and their contents, but this behaviour can be modified with the plugin decorators, with a very simple but extremely powerful syntax.

K-Eight was named after the presumed predecessor to K-9, the robot dog who for a time followed the Doctor around in the hit television series Doctor Who.  While K-Eight will never have K-9's abilities in handling laser weaponry and sensing the whereabouts of the Key of Time, I hope that you'll have fun using him.

## How do I use K-Eight?
Firstly, you'll need Python 2.7.x, which is available [here][pydownload].  Then download one of the two files in the header above and unzip it somewhere sensible.  Navigate to that folder, and run the command:

``` bash
~ $ python keight.py --new_config
```

This will create the file `config.yml`.  Edit that file to represent your chosen preferences and save.  Finally, run the following command:

``` bash
~ $ python keight.py
```
    
Now log onto the irc server that you connected K-Eight to, and play.

[pydownload]: <http://www.python.org/getit/releases/2.7.4/#download>