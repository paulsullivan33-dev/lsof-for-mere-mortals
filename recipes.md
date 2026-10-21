# Recipes

**Scope:** the everyday set, each one a
question in the words it's actually asked,
the command, and the captured answer it
produces. Every recipe was run in the lab;
the chapter numbers point at the full
captures.

## "Something is on this port and my service can't start"

```
$ lsof -iTCP:8734 -sTCP:LISTEN
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22428 root    3u  IPv4 857701      0t0  TCP localhost:8734 (LISTEN)
```

Chapter 5. The pid is the negotiation: stop
it, reconfigure it, or pick another port —
but identify it first with `ps` (the
*Watching Your System* guide) before killing
anything; a listener is often a service
someone else is using. Add `-iUDP:8734` if
the squatter might be a UDP socket — the two
protocols have separate namespaces and both
can hold "the same" port number.

## "The disk is full but du can't find it"

```
$ lsof +L1
COMMAND   PID USER   FD   TYPE DEVICE  SIZE/OFF NLINK    NODE NAME
python3 22406 root    3r   REG   0,86 209715200     0 7484178 /home/hatch/workspace/lsof-lab/tree/big/big.bin (deleted)
```

Chapter 4, the centerpiece as a one-liner.
Deleted-but-open files, sizes in the
SIZE/OFF column, biggest first by eye. The
fix is the holder closing or restarting —
and the proof afterwards is `df` giving the
space back, not lsof going quiet (though in
the lab it did both).

## "This directory won't delete / unmount — it's busy"

Two different holds, two questions. Who is
*standing* in it (cwd) or holding the
directory itself:

```
$ lsof /home/hatch/workspace/lsof-lab/tree/sub
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
sleep   22375 root  cwd    DIR   0,86       16 7484148 /home/hatch/workspace/lsof-lab/tree/sub
```

And who holds anything *under* it:

```
$ lsof +D /home/hatch/workspace/lsof-lab/tree
```

(three rows in chapter 3 — the tail, the
holder, the sleeper). Chapter 3 has the
cost warning: aim `+D` at the smallest tree
that covers the question. A forgotten shell
sitting in a directory with its cwd is the
usual culprit, and the fix is `cd` out, not
a kill.

## "What is this daemon actually holding?"

```
$ lsof -p 22347
```

Chapter 2's table: files, sockets, cwd,
executable, libraries — the process's whole
open world in one listing. Skim discipline:
the `mem` rows are almost never the story;
the numbered descriptors are. Cut them with
a `-d` exclusion list (each item negated
with `^`, the chapter 6 grammar), captured
against a planted holder:

```
$ lsof -a -p 25152 -d ^mem,^cwd,^rtd,^txt
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
python3 25152 root    0r   CHR    1,3      0t0       4 /dev/null
python3 25152 root    1w   CHR    1,3      0t0       4 /dev/null
python3 25152 root    2w   REG   0,86       70 7490068 /home/hatch/workspace/lsof-lab/transcripts/s12-slicing-noise.txt
python3 25152 root    3r   REG   0,86        9 7484200 /home/hatch/workspace/lsof-lab/tree/script.txt
python3 25152 root    4u   REG   0,86       10 7484150 /home/hatch/workspace/lsof-lab/tree/both.txt
[exit 0]
```

What survives is exactly what the process
opened for itself: the standard streams and
its two planted files.

## "Which process writes this log?"

```
$ lsof /home/hatch/workspace/lsof-lab/tree/notes.log
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
tail    22329 root    3r   REG   0,86       23 7484136 /home/hatch/workspace/lsof-lab/tree/notes.log
```

Chapter 1's move, with the FD letter doing
the talking: `3r` is a *reader* (here a
`tail -f` watching the log). A writer wears
`w` or `u` — in chapter 2's planted set,
`4w` on `write.txt`. If two processes hold
the log, one reading and one writing, the
letters separate them at a glance.

## "A connection to that host — whose is it?"

```
$ lsof -i :8734
```

Chapter 5's four-row table is the pattern:
listener, the accepted server-side socket,
and the client's row, the NAMEs mirrored
(`8734->59048`, `59048->8734`). On a real
machine, `lsof -i @dbhost` or a grep of
`lsof -i` output for the far address finds
the local end; the pid column names the
owner.

## "Show me just the interesting part, repeatedly"

```
$ lsof -r 2 -i :8734
```

Chapter 7: snapshots every 2 seconds with
`=======` between them — for the connection
that exists only while the cron job runs,
or the holder that appears at the moment of
failure. Bound it with `timeout` when
sampling for a record.
