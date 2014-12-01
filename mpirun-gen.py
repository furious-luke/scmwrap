#!/usr/bin/env python

import sys, os, subprocess
import smtplib
from email.mime.text import MIMEText

EMAIL_SUBJECT=''
EMAIL_FROM=''
EMAIL_TO=''

# Helps when using outdated Python.
def check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return output

class OptionParseError(Exception):

    def __init__(self, line, rest):
        self.line = line
        self.rest = rest

def handle_error(cmds, msg):
    cmd = ' '.join(cmds)
    if EMAIL_TO:
        msg += 'Command line: %s\n'%cmd
        mail = MIMEText(msg)
        mail['Subject'] = EMAIL_SUBJECT
        mail['From'] = EMAIL_FROM
        mail['To'] = EMAIL_TO
        s = smtplib.SMTP('localhost')
        s.sendmail(mail['From'], [mail['To']], mail.as_string())
        s.quit()
    print cmd
    sys.exit(0)

def split_options(line):
    opts = []
    ii = 0
    jj = 1
    while jj < len(line) and line[ii] == '-':
        while jj < len(line) and line[jj] not in ',<' and not line[jj].isspace():
            jj += 1
        opts.append(line[ii:jj].strip())
        if jj == len(line) or line[jj] == '<':
            break
        while jj < len(line) and (line[jj].isspace() or line[jj] in ','):
            jj += 1
        if jj + 1 < len(line) and line[jj] == '-' and line[jj + 1].isspace():
            jj = len(line)
        ii = jj
    return opts, line[jj:]

def count_args(line):
    n_args = 0
    ii = 0
    while ii < len(line):
        if line[ii] == '<':
            while ii < len(line) and line[ii] != '>':
                ii += 1
            ii += 1
            n_args += 1
        else:
            while ii < len(line) and not line[ii].isspace():
                ii += 1
            n_args += 1
        while ii < len(line) and line[ii].isspace():
            ii += 1
    return n_args

def update_man_path(bin, impl):
    impl_subdirs = {
        'mpich': os.path.join('share', 'man'),
        'mpich2': os.path.join('share', 'man'),
        'openmpi': os.path.join('share', 'man'),
        'mvapich': 'man',
        'mvapich2': os.path.join('share', 'man'),
    }
    subdir = impl_subdirs.get(impl, os.path.join('share', 'man'))
    path = os.path.join(os.path.dirname(os.path.dirname(bin)), subdir)
    os.environ['MANPATH'] = ':'.join([path] + os.environ.get('MANPATH', '').split(':'))

def make_opt_dict(bin, impl):
    impl_bins = {
        'mpich': 'mpiexec',
        'mpich2': 'mpiexec',
        'openmpi': 'mpirun',
        'mvapich': 'mpiexec',
        'mvapich2': 'mpiexec',
    }
    run = impl_bins.get(impl, 'mpiexec')
    opt_dict = {}
    update_man_path(bin, impl)
    help_str = check_output(' '.join(['man', run, '|', 'col', '-bx']), stderr=subprocess.STDOUT, shell=True)
    lines = help_str.splitlines()
    line_ii = 0
    while line_ii < len(lines):
        line = lines[line_ii]
        line = line.rstrip()
        line_ii += 1
        first = len(line) - len(line.lstrip())
        line = line.lstrip()
        if len(line) > 1 and line[0] == '-' and first == 7 and line[1] != ' ':
            opts, rest = split_options(line)
            n_args = count_args(rest)
            opt_dict.update(dict([(o, n_args) for o in opts]))
            while line_ii < len(lines) and (len(lines[line_ii]) - len(lines[line_ii].lstrip())) > first:
                line_ii += 1

    # Hacks.
    if impl == 'mvapich':
        opt_dict['-nolocal'] = 0

    return opt_dict

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print 'Too few arguments.'
        sys.exit(1)

    bin = sys.argv[1]
    script = sys.argv[2]
    impl = sys.argv[3]
    cmds = [bin] + sys.argv[4:]

    if len(sys.argv[4:]) == 0:
        handle_error(cmds, 'Bad command line.\n')

    try:
        opt_dict = make_opt_dict(bin, impl)
    except OptionParseError as e:
        handle_error(cmds, 'Failed to parse options:\nLine: %s\nRest: %s\n'%(e.line, e.rest))

    ii = 1
    add = False
    while ii < len(cmds):
        opt = cmds[ii]
        if opt[0] != '-':
            add = True
            break
        ii += 1
        skip = opt_dict.get(opt, None)
        if skip == None:
            handle_error(cmds, 'Unknown option: %s\n'%opt)
        if ii + skip > len(cmds):
            handle_error(cmds, 'Bad command line.\n')
        if ii + skip == len(cmds):
            break
        while skip:
            if cmds[ii][0] == '-':
                handle_error(cmds, 'Suspected skipped option: %s\n'%cmds[ii])
            ii += 1
            skip -= 1
    if add:
        cmds.insert(ii, script)
    print ' '.join(cmds)
