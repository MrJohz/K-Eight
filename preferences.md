---
layout: default
---

## Configuration

K-Eight is configured with a `config.yml` file in the same directory as the program being run.  The file should be in standard [YAML markup][yaml].  This is an overview of all of the potential options and variations for a config file.

[yaml]: <http://www.yaml.org/spec/1.2/spec.html>

### Connection (required)            {#connection}

#### nick

The nickname for your bot.  This parameter is required.

#### server

The server the bot should connect to.  As the server may contain odd characters, this should be enclosed in quote characters.  This parameter is required.

#### port

An integer or string representing the port on the server that K-Eight should connect to.  If it is not stated, or is blank or a null value, it defaults to 6667.

#### password

The password that the bot should use to connect to the server (not any particular channel).  If this is blank or a null value, the bot will attempt to connect without a password.

#### channels

A list of the channels that the bot should attempt to join when it connects.  As the pound symbol ('#') is assumed to be a comment in YAML in certain situations, the channel name should be quoted in full (`"#channelname"`) or the pound symbol can be ommitted.

### Admin (required)                 {#admin}

#### owner

Your name, nick, or some other identifier of your choosing.  This should allow others to contact you if the bot stops working or is disturbing others.  This parameter is required.

#### admins

A list of admins.  If `use_ident` is true, this should be the identified names of the admins if this differs from popular nicks.  (e.g. a person with the nicks "Monty", "MontyPython" and "MP" all grouped to the account "MontyPython", then you should put "MontyPython".  If this parameter is not included, it defaults to a list containing just the value of `owner`.

#### command_key

A one-character symbol that prefaces all commands.  This defaults to '.', but other popular characters include '!' and '$'.

#### plugins_folder

The directory where the plugins can be found.  The bot will follow relative paths from the directory that the script is located, rather than where it is run from.  This defaults to "./plugins"

#### use_ident

This determines if the bot should use a built-in identification service to determine if a user is logged in to a NickServ-like account.  If this is False, then anyone with the same nick as an admin will be considered an admin, and everyone will be assumed to be identified.  This is understandably more dangerous, but necessary for servers where there are no nick-managing services.  This defaults to True

### NickServ (optional)              {#nickserv}

#### name

The name that the bot should use when connecting to NickServ.  (Some services allow a user to log into an account whilst under a different nick - this facilitates that.)  If this is None or not present, then the bot will assume that it is registered under a NickServ account of the same name.

#### password

The password for the NickServ service.  If this is None or not present, then the bot will not attempt to connect to NickServ.

#### command

A command to be issued once the bot is connected.  This should principally be used to deal with services such as Q which operate slightly differently to NickServ, or have different names.

### Logging (optional)               {#logging}
This should be a list of output loggers.  See [logging][] for more details.
[logging]: <logging>


### Modules (optional)               {#modules}
#### exclude
This should be a list of modules that should not be loaded.  The default `config.yml` includes the `admin` and `logging` (until it is fixed) modules.  If this is omitted, all modules are loaded.

#### include
This includes a list of modules that should be loaded.  If this module exists and is not a null value, then no modules will be loaded except those that are on this list.  Modules that are on the exclude list will still not be loaded.

#### chanexclude
Doesn't work.

#### chaninclude
Doesn't work.