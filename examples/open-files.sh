#!/usr/bin/env bash
# open-files.sh PID -- list a process's open files, one per line:
# PID, FD, NAME. A worked example of parsing lsof's field output (-F).
#
# lsof -F emits one field per item, each introduced by a single letter:
# p = process ID, f = file descriptor, n = name. With -F0 the fields are
# separated by NUL bytes instead of newlines, so filenames containing
# spaces or newlines survive the trip. Here they are turned back into
# lines with tr and walked with awk.
set -u

pid=${1:?usage: open-files.sh PID}

lsof -Fpfn -p "$pid" 2>/dev/null | tr '\0' '\n' | awk '
    /^p/ { p = substr($0, 2) }
    /^f/ { f = substr($0, 2) }
    /^n/ { print p, f, substr($0, 2) }
'
