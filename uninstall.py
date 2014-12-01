#!/usr/bin/env python

##
## Uninstall the SCM wrappers.
##

import sys, os, subprocess, argparse, shutil
from scmwrap import *

class Missing(Exception):
    pass

def uninstall(bin, impl):
    orig_fn = bin + '.orig'
    if not os.path.exists(orig_fn):
        raise Missing
    shutil.move(orig_fn, bin)

if __name__ == '__main__':

    parser = argparse.ArgumentParser('uninstall SCM wrappers')
    parser.add_argument('-i', '--init', default='.', help='initial path')
    parser.add_argument('--dry-run', action='store_true', help='don\'t execute commands')
    args = parser.parse_args()

    for bin, impl in iter_bins(args.init):
        print bin
        print '  %s implementation'%impl
        if not already_done(bin):
            print '  not installed'
        elif not args.dry_run:
            try:
                uninstall(bin, impl)
                print '  uninstallation complete'
            except Missing:
                print '  ** cannot uninstall, original is missing'
