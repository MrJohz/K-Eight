"""A very *very* simple module for dealing with command-line parsing when the
only things you need to worry about are arguments and switches.  Uses
POSIX-esque command-line splitting, because non-POSIX-esque command-line
splitting is silly."""

import shlex

class CloptError(Exception):
    pass

class Switch(list):
    def __init__(self, names, name=None):
        self._name = name
        self.extend(names.split('|') if '|' in names else [names])
        self.required = False
        if self[-1].endswith('='):
            self.required = 'required'
            self[-1] = self[-1][:-1]
        elif self[-1].endswith(':'):
            self.required = None
            self[-1] = self[-1][:-1]
        
        if any(i.endswith('=') or i.endswith(':') for i in self):
            raise CloptError("Could not resolve switches")
    def shorts(self):
        optstring = '|'.join(opt for opt in self if len(opt) == 1)
        if self.required == 'required':
            optstring += '='
        elif self.required is None:
            optstring += ':'
        return Switch(optstring, name=self.name())
    
    def longs(self):
        optstring = '|'.join(opt for opt in self if len(opt) > 1)
        if self.required == 'required':
            optstring += '='
        elif self.required is None:
            optstring += ':'
        return Switch(optstring, name=self.name())
    
    def string(self):
        optstring = '|'.join(self)
        if self.required == 'required':
            optstring += '='
        elif self.required == 'optional':
            optstring += ':'
        return optstring
    
    def name(self):
        if self._name is None:
            return self[0]
        else:
            return self._name
    
    def compare(self, l, safe):
        for i in l:
            if i[0] in self and self.required is None:
                yield i
            elif i[0] in self and bool(i[1]) == bool(self.required):
                yield i
            elif i[0] in self and not safe:
                text = "Invalid optional argument for {j!r}"
                raise CloptError(text.format(j=i[0]))

def _split_equals(string, split='='):
    if split in string:
        return tuple(string.split(split, 1))
    else:
        return string, ''

def get_args(args, gnu=False):
    """A slight upgrade on getopt"""
    try:
        optargs = shlex.split(args)
    except AttributeError:
        optargs = args
    except ValueError:
        raise CloptError("Invalid arguments ({exc})".format(exc=exc))
    shrt_opts = []
    long_opts = []
    args = []
    args_only = False
    for token in optargs:
        if token == '--':
            if gnu:
                args_only = True
            else:
                args_only = True
                args.append(token)
        elif token.startswith('--') and not args_only:
            long_opts.append(_split_equals(token[2:]))
        elif token.startswith('-') and not args_only:
            o, a = _split_equals(token[1:])
            a = o[1:] + a
            shrt_opts.append((o[0], a))
        else:
            args_only = True
            args.append(token)
    return tuple(shrt_opts), tuple(long_opts), tuple(args)

def associate_args(shorts, longs, args, switches, arguments, safe=False):
    opts = list(shorts) + list(longs)
    args = list(args)
    arguments = list(arguments) 
    switches = [Switch(i) for i in switches]
    ret_switches = {}
    ret_args = {}
    done = []
    for switch in switches:
        done.extend(i[0] for i in switch.compare(opts, safe))
        results = [i[1] for i in switch.compare(opts, safe)]
        if results:
            ret_switches[switch.name()] = results
    if not set(done) == {opt[0] for opt in opts} and not safe:
        raise CloptError("Unrecognised options")
    
    if arguments[-1].endswith('*'):
        rest_arg = arguments.pop(-1)[:-1]
    else:
        rest_arg = None
    
    if len(args) < len(arguments) and not safe:
        raise CloptError("Missing required arguments")
    
    args, arguments = args[::-1], arguments[::-1]
    for i in xrange(len(arguments)):
        ret_args[arguments.pop()] = args.pop()
    
    if rest_arg is not None:
        ret_args[rest_arg] = args
    elif not safe:
        raise CloptError("Too many arguments")
    return ret_switches, ret_args
    
    
    

    
'''
def count(args, switch='v'):
    """Counts verbosity flags."""
    opts, args = get_optarg(args)
    return sum(len(opt[0]) for opt in opts if all(l == switch for l in opt[0]))
'''

def clopt(args, switches, arguments, safe=False, gnu=False):
    s, l, a = get_args(args, gnu)
    return associate_args(s, l, a, switches, arguments, safe)