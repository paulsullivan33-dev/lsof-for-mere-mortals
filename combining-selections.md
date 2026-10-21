# Combining Selections

**Scope:** how lsof adds selections up —
the OR default, `-a` for AND, lists and `^`
exclusions inside one selection, `-c` by
command name — with the misleading cases
captured, including one this guide's own
lab walked into.

## The rule: selections add up

Every lsof selection you have used so far is
a filter: a name, `-p`, `-i`, `-u`, `-c`,
`-d`. What the earlier chapters politely
didn't stress: when you give **several**
selections, a row needs to match only
**one** of them. Selections are ORed. The
lab demonstrates with two plants that share
nothing — holder A (pid 22452) holds a file
and no sockets; listener B (pid 22453) holds
port 8734 and no lab files:

```
[planted: holder A pid 22452 (a file, no sockets); listener B pid 22453 (port 8734, no lab files); tail pid 22454]
$ lsof -p 22452 -i :8734
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF                NODE NAME
python3 22452 root  cwd    DIR   0,86       72             7483797 /home/hatch/workspace/lsof-lab
...
python3 22452 root    3r   REG   0,86        6             7484186 /home/hatch/workspace/lsof-lab/tree/logic.txt
python3 22453 root    3u  IPv4 859175      0t0                 TCP localhost:8734 (LISTEN)
python3 22453 root    4u  IPv4 859176      0t0                 UDP localhost:8734 
[exit 0]
```

Asked for "pid 22452, port 8734," lsof
delivered *everything pid 22452 holds*
(15 rows) *plus everything on port 8734*
(B's 2 rows) — because that's what OR means.
If what you meant was "what does 22452 hold
**on port 8734**," the answer is a different
command.

## -a: make it AND

`-a` switches the combination to AND — a row
must satisfy *every* selection:

```
$ lsof -a -p 22452 -i :8734
[exit 1]
$ lsof -a -p 22453 -i :8734
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22453 root    3u  IPv4 859175      0t0  TCP localhost:8734 (LISTEN)
python3 22453 root    4u  IPv4 859176      0t0  UDP localhost:8734 
[exit 0]
```

The empty first answer is the *correct*
answer: A holds nothing on that port, and
the exit 1 says so. This is why chapter 2's
`-d` slices were written `lsof -a -p … -d …`
— the `-a` there was not ceremony.

## The trap this lab walked into

`-d` is a selection like any other, so it
ORs too. An early lab run asked for "the
cwds of pids A and B" as:

```
$ lsof -p 22452,22453 -d cwd
```

and got a screenful: **every process's cwd
row on the machine** (that selection, alone,
matches them all) *plus the complete tables
of both pids* (the other selection, alone,
matches those) — systemd's cwd, the lab
shell's, a row of `unknown` entries for
processes in another corner of the build
sandbox, the lot. The capture is kept whole
in the lab transcripts (session s07) as the
exhibit. The fix is the same `-a` fence:

```
$ lsof -a -p 24265,24266 -d cwd
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
python3 24265 root  cwd    DIR   0,86       72 7483797 /home/hatch/workspace/lsof-lab
python3 24266 root  cwd    DIR   0,86       72 7483797 /home/hatch/workspace/lsof-lab
[exit 0]
```

Exactly two rows. (New plants, new pids —
the rerun is its own session, s07b.) When an
lsof command prints far more than the
question asked, the missing `-a` is the
first suspect, every time.

## Inside one selection: lists and ^

Within a *single* selection, commas make a
list (also an OR — any item may match), and
`^` at the front of an item excludes it:

```
$ lsof -a -p 24265,^24266 -d cwd
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
python3 24265 root  cwd    DIR   0,86       72 7483797 /home/hatch/workspace/lsof-lab
[exit 0]
```

"A and B" gave two rows; "A and not-B" gave
one. The same list grammar works in `-u`
(users) and `-c` (commands), and the
exclusion form is how you say "this port,
but not that process" without a pipeline.

## By command name: -c

`-c` selects by the COMMAND column — exact
name, or a `/regex/` between slashes:

```
$ lsof -c tail
COMMAND   PID USER   FD      TYPE DEVICE SIZE/OFF                NODE NAME
tail    22454 root  cwd       DIR   0,86       72             7483797 /home/hatch/workspace/lsof-lab
...
tail    22454 root    3r      REG   0,86        7             7484187 /home/hatch/workspace/lsof-lab/tree/logic.log
tail    22454 root    4r  a_inode   0,17        0                  59 inotify
[exit 0]
```

The planted `tail`'s whole table from its
name alone. Two cautions ride along: the
COMMAND column is the executable's name
truncated to 9 characters (`systemd-j`,
`redis-ser` in earlier captures), so `-c`
matches that truncated name; and a *script*
runs under its interpreter's name — the
lab's `hold.py` processes are `python3` to
lsof, which is why the chapters select them
by pid. `-c` shines for daemons with real
names of their own.

Summary of the logic, worth memorising:
**different selection types add (OR);
`-a` intersects (AND); inside one selection,
commas add and `^` subtracts.** Most
"lsof printed the wrong thing" stories are
the first clause.
