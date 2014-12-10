#!/bin/bash

N_CTXS=`cat /sys/class/infiniband/qib0/nctxts`
N_FCTXS=`cat /sys/class/infiniband/qib0/nfreectxts`
IFS='.' read -ra HOST <<< "`hostname`"
N_CPUS=`cat /proc/cpuinfo | grep cpuid | wc -l`
MY_JOB_ID=$(echo $PBS_JOBID | egrep -o '[0-9]+')
if [ ! -z $MY_JOB_ID ]; then
    N_RCPUS=`pbsnodes $HOST | sed -n 's/jobs = \(.*\)/\1/p' | egrep -o "$MY_JOB_ID" | uniq -c | awk '{print $1}'`
    X="$(echo "$N_RCPUS*$N_CTXS/$N_CPUS" | bc)"
    X=$(($X>1?$X:1))
    PSM_SHAREDCONTEXTS_MAX=$(($X<$N_FCTXS?$X:$N_FCTXS))
    export PSM_SHAREDCONTEXTS_MAX
fi

# echo $HOST
# echo MY_JOB_ID: $MY_JOB_ID
# echo N_CTXS: $N_CTXS
# echo N_FCTXS: $N_FCTXS
# echo N_CPUS: $N_CPUS
# echo N_RCPUS: $N_RCPUS
# echo PSM_SHAREDCONTEXTS_MAX: $PSM_SHAREDCONTEXTS_MAX

# It seems some mpirun implementations are happy to locate binaries
# in the pwd without using "./". Check for an executable file of the
# correct name and prefix accordingly.
if [[ -x "$1" ]]; then
    CMD=./$1
else
    CMD=$1
fi

# Call actual program.
exec $CMD "${@:2}"
