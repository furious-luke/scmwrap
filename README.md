# Shared-Contexts-Maximum Wrappers

## Purpose

QLogic InfiniBand adaptors provide a number of hardware
contexts used to provide highspeed connections to
other nodes in cluster computing environments. When the
number of MPI ranks used on a node is less than or equal
to the available hardware contexts then everything works
as expected. When there are more ranks than contexts, however,
a mechanism needs to be in place to allow sharing of
contexts efficiently; when this is not the case the following
is the usual result:

```
can''t open /dev/ipath, network down (err=26)
```

One solution is to force all ranks to share contexts regardless
of node utilisation. This will prevent any connection failures,
but will also reduce performance.

An improved solution is to assign more hardware contexts to
jobs that are running more ranks on a node. However this can
also be somewhat painful, depending on the policies surrounding
queue resource specification.

The purpose of these scripts is try to automate setting
`PSM_SHAREDCONTEXTS_MAX` to optimal values. The scripts try not
to rely on parameters, instead reading as much information as
possible from standard locations.

## Important Note

These scripts have really only been tested on one machine, use
at your own risk.

## Usage

Place the contents of the package somewhere accessible by
the users of the cluster, typically in a shared folder, say
for example `/usr/local`:

```bash
cd /usr/local
mkdir scmwrap
cd scmwrap
tar xzf scmwrap.tgz
```

Then, to install the wrappers to all installations of MPI
below a certain directory, run:

```bash
./install.py -i <base-directory>
```

To uninstall:

```bash
./uninstall.py -i <base-directory>
```

## Email on Failure

In order to place the `set_scm.sh` script in the right position
in the mpirun line, a bit of parsing is required. This will
inevitably fail on some more creative mpirun commands. The system
is designed to fall back to the original mpirun line to prevent
system-wide failure, and can optionally email an administrator.

To enable emailing edit the `mpirun-gen.py` file, there are three
lines near the beginning of the file that control email.

## Bug Reporting

Please let me know if anything fails by either reporting an issue
via github, or contacting me at `furious.luke@gmail.com`.
