---
layout: default
---

> K-Eight is fast, easy to extend, friendly, and designed for everything from chatting to channel management.  Have fun.

## What is K-Eight?
K-Eight is a Python IRC bot designed by [myself][johz] using Evan Fosmark's [IRCUtils][ircutils] to deal with the IRC abstractions.  It is currently in the process of being padded out with extra features such as IRC logging and the whole host of commands and triggers that one expects from a fully-featured IRC bot.  However it is already a powerful tool, with its own internal logging system and a powerful toolkit.

K-Eight is designed around the principle of plugins.  Plugins can be included and excluded easily from a single YAML configuration file, but they can also be modified and added to by anyone who understands how to write a function in Python.  K-Eight will automatically recognise plugin scripts and their contents, but this behaviour can be modified with the plugin decorators, with a very simple but extremely powerful syntax.

K-Eight was named after the presumed predecessor to K-9, the robot dog who for a time followed the Doctor around in the hit television series Doctor Who.  While K-Eight will never have K-9's abilities in handling laser weaponry and sensing the whereabouts of the Key of Time, I hope that you'll have fun using him.

[johz]: <http://johz.wordpress.com>
[ircutils]: <http://dev.guardedcode.com/projects/ircutils/>

## How do I use K-Eight?
*This is just a quickstart.  For the full story, you might want to read the [documentation][commandline] of K-Eight's command-line interface.*

Firstly, you'll need Python 2.7.x, which is available on the [python.org website][pydownload].  Then download one of the two files in the header above and unzip it somewhere sensible.  Navigate to that folder, and run the command:

{% highlight bash %}
~ $ python keight.py --new_config
{% endhighlight %}

This will create the file `config.yml`.  Edit that file to represent your chosen preferences and save.  Finally, run the following command:

{% highlight bash %}
~ $ python keight.py
{% endhighlight %}
    
Now log onto the irc server that you connected K-Eight to, and play.  It's just that simple.

[commandline]: <./docs>
[pydownload]: <http://www.python.org/getit/releases/2.7.4/#download>

## What can K-Eight do?
K-Eight has many triggers, but the most obvious one is the .command syntax popularised by bots such as Phenny.  Try out some of the following to get started:

* `.help` - Provides some help and information.
* `.tell` - Allows you to leave messages for others.
* `.c` - Allows you to do calculations.
* `.decide` - Makes tough decisions easy.
* `.rr` - For when you just want to play some russian roulette with friends.

For more thorough documentation, check out the [commands][] page, and have a look through there.  Or, if you're bored already, check out the next section of this brief introduction.

[commands]: <./commands>

## What else can I do with K-Eight?
Now you're asking the right sort of questions.  Try these three things on for size:
1. Play with the preferences in `config.yml`.  Go wild, and if you really manage to break things, just run K-Eight with the `--new_config` switch again to produce a new configuration file.  You might want to check out our [preferences][] page.
2. Write your own command.  Ultimately, if you can write a function you can write a K-Eight command.  An overview of what one of those functions should look like can be found in the [tutorial][].
3. Fork the Repo.  Because while you can have fun with your own version of K-Eight, how much more awesome would it be if your modifications were used by everyone?  Speaking as a lazy coder, I think it would be *really* awesome, and you should totally get on with it.  K-Eight can be found on Github via the link at the top of the page, or by clicking [here][github].

[preferences]: <./preferences>
[tutorial]: <./tutorial>
[github]: <https://github.com/MrJohz/K-Eight>