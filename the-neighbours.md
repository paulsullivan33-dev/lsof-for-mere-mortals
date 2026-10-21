# The Neighbours

**Scope:** the tools that overlap lsof —
`fuser`, which answers "who" more bluntly
and can act on the answer; `/proc/<pid>/fd`,
the raw evidence lsof itself reads; `ss`,
revisited from chapter 5; and `netstat`,
the retired ancestor all of them replaced.

## fuser: who, with a trigger

`fuser` answers a narrower question — which
processes are using this file or this
socket — and prints just pids. The `-v`
form names them properly. The lab's tail,
asked both ways:

```
$ fuser -v /home/hatch/workspace/lsof-lab/tree/notes.log
                     USER        PID ACCESS COMMAND
/home/hatch/workspace/lsof-lab/tree/notes.log:
                     root      22552 f.... tail
[exit 0]
$ fuser -v 8734/tcp
                     USER        PID ACCESS COMMAND
8734/tcp:            root      22553 F.... python3
[exit 0]
```

Pid 22552 is the planted tail, pid 22553
the planted listener — both check out. The
ACCESS column is fuser's own dialect:
`f` is an open file (the tail's read of the
log), and a socket is reported `F` — psmisc
counts it on the write side. Other letters
cover cwd (`c`), a running executable
(`e`), a root directory (`r`), a mapped
library (`m`): a compressed cousin of
lsof's FD column, with no sizes, no inode
numbers, no full tables. For a quick "who
has this file" on a machine without lsof,
fuser is a fine answer; for anything
diagnostic, you end up wanting the table.

And fuser has the option lsof deliberately
lacks: `-k`, **kill the processes using
this**. The lab ran it against the planted
tail:

```
$ fuser -k /home/hatch/workspace/lsof-lab/tree/notes.log
/home/hatch/workspace/lsof-lab/tree/notes.log: 22552
[exit 0]
$ lsof /home/hatch/workspace/lsof-lab/tree/notes.log
[exit 1]
$ pgrep -a tail
[exit 1]
```

Dead, verified two ways (lsof silent, no
tail process anywhere). Treat `-k` the way
you'd treat any pre-aimed kill: it sends
SIGKILL by default — no cleanup, no
shutdown hooks — to *every* process the
file matches, which for a popular file can
be a crowd. Identify with lsof first,
kill by pid with intent, and let `-k` stay
the lab trick it is here. (The
`22552 Killed` shell notice in the raw
transcript is the lab shell reporting its
own child's death, not fuser talking.)

## /proc/<pid>/fd: the evidence itself

Everything lsof prints about a process
comes out of `/proc`, and the descriptor
table is sitting there as symlinks for
anyone (with permission — chapter 8) to
read. The same tail, raw:

```
$ ls -l /proc/22552/fd
total 0
lr-x------ 1 root root 64 Oct 21 01:15 0 -> /dev/null
l-wx------ 1 root root 64 Oct 21 01:15 1 -> /home/hatch/workspace/lsof-lab/transcripts/s10-neighbours.txt
l-wx------ 1 root root 64 Oct 21 01:15 2 -> /home/hatch/workspace/lsof-lab/transcripts/s10-neighbours.txt
lr-x------ 1 root root 64 Oct 21 01:15 3 -> /home/hatch/workspace/lsof-lab/tree/notes.log
lr-x------ 1 root root 64 Oct 21 01:15 4 -> anon_inode:inotify
[exit 0]
```

Line it up against chapter 2's table: fd 3
is the log, fd 4 is the inotify watch
(`anon_inode:inotify` here, `a_inode …
inotify` in lsof's rendering), 0/1/2 are the
standard streams, and the `r`/`w` in the
symlink permissions are where lsof's access
letters come from. `readlink /proc/PID/cwd`
and `…/exe` gave chapter 2 its cross-checks.
What raw `/proc` doesn't do: search. There
is no `ls` that answers "who holds this
file" — that requires walking every pid's
fd directory and matching inodes, which is
precisely the work lsof exists to do. Read
`/proc` to verify; query with lsof.

## ss, one more time

Chapter 5 did the head-to-head; the verdict
in one line each way. For socket-shaped
questions — states, queues, timers, every
connection on the box — `ss` is the native
tool and the faster design (a direct kernel
query versus a per-process scan). For "the
process as a whole" questions — its files,
its cwd, its deleted-but-open log — only
lsof has the table. Working fluency is
both, chosen per question, and the two
agreeing (as they did on pid 22428, fd 3)
is what a verified answer looks like.

## netstat: the ancestor

The build machine does have it:

```
$ command -v netstat
/usr/bin/netstat
[exit 0]
```

`netstat` is the tool `ss` replaced: same
socket questions, answered from a slower
`/proc` scrape, output format frozen a
generation ago. It lingers in old runbooks
and older administrators' fingers. Nothing
in this guide needs it, and the mapping is
one-to-one enough to state plainly:
`netstat -ltnp` is `ss -ltnp`. It is named
here so a reader who meets it in the wild
knows it's the same territory, documented
rather than taught — the series teaches the
current tools.
