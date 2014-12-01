import sys, os, subprocess, argparse, shutil

class FailedIdentify(Exception):
    def __init__(self, bin):
        self.bin = bin

def already_done(bin):
    with open(bin, 'r') as f:
        f.readline()
        return f.readline().strip() == '# scm wrapper'

def identify(bin):
    id_dir = os.path.dirname(os.path.dirname(bin))
    if 'openmpi' in id_dir:
        return 'openmpi'
    elif 'mpich2' in id_dir:
        return 'mpich2'
    elif 'mpich' in id_dir:
        return 'mpich'
    elif 'mvapich2' in id_dir:
        return 'mvapich2'
    elif 'mvapich' in id_dir:
        return 'mvapich'
    elif 'mpiexec' in id_dir:
        return 'mpiexec'
    else:
        raise FailedIdentify(bin)

def iter_bins(start):
    for path, dirs, files in os.walk(start):
        for f in files:
            if f in ['mpirun', 'mpiexec']:
                bin = os.path.join(path, f)
                try:
                    yield bin, identify(bin)
                except FailedIdentify as e:
                    print '** failed to identify: %s'%e.bin
