#!/usr/bin/env python

##
## Install the SCM wrappers.
##

import sys, os, subprocess, argparse, shutil
from scmwrap import *

template = '''#!%s
# scm wrapper
CMD=`%s %s %s %s "$@"`
IFS=' ' read -a CMDARRAY <<< "$CMD"
exec "${CMDARRAY[@]}"
'''

class AlreadyExists(Exception):
    pass

def install(shell, gen, bin, impl, script):
    orig_fn = bin + '.orig'
    if os.path.exists(orig_fn):
        raise AlreadyExists
    shutil.move(bin, orig_fn)
    with open(bin, 'w') as f:
        f.write(template%(shell, gen, orig_fn, script, impl))
    os.chmod(bin, os.stat(orig_fn).st_mode)

if __name__ == '__main__':

    parser = argparse.ArgumentParser('install SCM wrappers')
    parser.add_argument('-s', '--script', default=None, help='script to insert')
    parser.add_argument('-i', '--init', default='.', help='initial path')
    parser.add_argument('--dry-run', action='store_true', help='don\'t execute commands')
    args = parser.parse_args()

    if args.script is None:
        args.script = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'set_scm.sh')
    if not os.path.exists(args.script):
        print '  ** failed to find script'
        sys.exit(1)

    gen = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mpirun-gen.py')
    if not os.path.exists(gen):
        print '  ** failed to find generator'
        sys.exit(1)

    shell = subprocess.check_output(['which', 'bash']).strip()
    if not os.path.exists(shell):
        print ' ** failed to find shell'
        sys.exit(1)

    for bin, impl in iter_bins(args.init):
        print bin
        print '  %s implementation'%impl
        if already_done(bin):
            print '  already installed'
        elif not args.dry_run:
            try:
                install(shell, gen, bin, impl, args.script)
                print '  installation complete'
            except AlreadyExists:
                print '  ** cannot install, copy already exists'
