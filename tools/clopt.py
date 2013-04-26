"""A very *very* simple module for dealing with command-line parsing when the
only things you need to worry about are arguments and switches.  Uses
POSIX-esque command-line splitting, because non-POSIX-esque command-line
splitting is silly."""

import shlex

def clopt(args, switches=None, preserve_all_opts=False):
    switches = ['-', '--'] if switches is None else switches
    optargs = shlex.split(args)
    opts = []
    args = []
    for opt in optargs:
        for switch in switches:
            if opt.startswith(switch):
                opts.append(opt[len(switch):])
                break
        else:
            args.append(opt)
    opts_dict = []
    for opt in opts:
        if '=' in opt:
            opt, optarg = opt.split('=', 1)
            opts_dict.append((opt, arg))
        else:
            opts_dict.append((opt, ''))
    args = tuple(args)
    if not preserve_all_opts:
        opts_dict = dict(opts_dict)
    else:
        opts_dict = tuple(opts_dict)
    return opts_dict, args

def verbose(args, verbose='v', switches=None):
    opts, args = clopt(args, switches, preserve_all_opts=True)
    return sum(len(opt[0]) for opt in opts if all(l == verbose for l in opt[0]))