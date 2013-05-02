---
layout: default
---

## Documentation

{% highlight bash %}
~ $ python keight.py [--quiet | -q] [--version] [--new_config]
    [--nick -n <NICK>] [--server -s <SERVER>] [--port -p <PORT>]
    [--pword <PASS>] [-h | --help] [--]
    [ channel1 [ channel2 [ channel3 [...]]]]
{% endhighlight %}

### Descriptions
> `--quiet`
> 
> `-q`

All logging to stdout/stderr will be redirected to the files `stdout.log` and `stderr.log` respectively.

> `--version`

Prints the current version and exits.  (The current version can be found in the `VERSION.txt` file in the main directory.)

> `--new_config`

Creates a new `config.yml` file and exits.  If this file exists it is overwritten, so be careful when using this switch.

> `--nick=NICK`
>
> `-n=NICK`

Starts K-Eight as usual, but with the nickname `NICK` instead of the nickname found in the configuration file.

> `--server=SERVER`
>
> `-s=SERVER`

Starts K-Eight as usual, but running on the server `SERVER` instead of the server found in the configuration file.

> `--port=PORT`
>
> `-p=PORT`

Starts K-Eight as usual, but connects to port `PORT` instead of the port found in the configuration file.

> `--pword=PASS`

Starts K-Eight as usual, but connects to the server using the password `PASS` instead of the password found in the configuration file.

> `-h`
>
> `--help`

Shows a help message and exits.

> `--`

K-Eight will not interpret any more arguments as options.

> `channel1 [...]`

Each other argument will be interpreted as a channel to join once connected to the server.  K-Eight will automatically preface the channel name with a pound sign ('#').

### Examples

{% highlight bash %}
# Will create a new config.yml file
~ $ python keight.py --new_config
# Will connect to the default server using port 6663
~ $ python keight.py -p=6663 -s"irc.freenode.net"

# The following will connect to channel1
~ $ python keight.py channel1
{% endhighlight %}

### Further Notes
K-Eight does utilise a `#! python` line, but you may wish to modify this to point to your specific Python interpreter.  However, this may mean on certain systems that including `python` in the command may not be necessary, and thus K-Eight could be run as follows:
{% highlight bash %}
~ $ keight.py
{% endhighlight %}
All of the above documentation and examples will still work using this method.