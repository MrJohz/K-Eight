---
layout: default
---


> K-Eight couldn't be here without the use of various packages, and the thoughts and writings of a number of people.

## What does K-Eight use?

K-Eight could not be here without the use of Evan Fosmark's [IRCUtils][], which provides a lot of the backend work of connecting and handling IRC messages.  The license for this package can be found in the [`ircutils/__init__.py`][ircutilslicense] file.  K-Eight also uses [PyYAML][] for dealing with the configuration files.

K-Eight's plugin system was reproduced with some variation from a post on LKJoel's blog:  <http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/>

[ircutils]: <http://dev.guardedcode.com/projects/ircutils/>
[ircutilslicense]: <https://github.com/MrJohz/K-Eight/blob/master/ircutils/__init__.py>
[pyyaml]: <http://pyyaml.org/>

## What inspired K-Eight?

The biggest inspiration, as is probably obvious, was Sean B. Palmer's Phenny.  Indeed, K-Eight was originally a fast-but-basic drop-in replacement for a certain channel's Phenny when the server it was hosted on died.  (Phenny, and the later Jenni, had a tendency to run slowly on our machines).  The ability to write plugins with just a simple function was extremely important to me.

If I'm talking about K-Eight's routes, I should also thank Solm, whose Ruby bot inspired my overly competitive ego to attempt to best his efforts.

## Anyone else?

GitHub for code hosting and for this site, Jekyll for this site, Solm for CSS help, Jason Long for the original site theme, the [Python IRC Channel][poundpython] ([#python@irc.freenode.net][python]) and other people who I've forgotten.

[poundpython]: <http://pound-python.org/>
[python]: <irc://irc.freenode.net/#python>