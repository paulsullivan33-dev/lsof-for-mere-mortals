# What lsof Is

**Scope:** the idea — a process's open files
as one table you can search — plus your
version, the size of the full answer, and
the first lab plant: a `tail` found from
nothing but the file it holds.

## Everything is a file, and it's a list

Unix-like systems hand a process almost
everything through the same door: the **file
descriptor**, a numbered handle. A document
gets one. So does the terminal the process
is attached to, the pipe feeding it, the
directory it's standing in, and each network
connection — a socket is reached through a
file descriptor too, even though no file on
any disk corresponds to it. "Open files,"
in lsof's sense, means *everything a process
currently holds a handle to*.

**lsof** — the name is the command, "list
open files" — walks every process and prints
one row per handle. That single table answers
the three questions this guide keeps asking:

- **Who has this?** A file, a directory, a
  port — name it, and lsof names the process.
- **What is this process holding?** Give a
  pid and get its whole open world.
- **Where did the space go?** A file can be
  deleted from every directory and still exist
  — as long as a process holds it open.
  Chapter 4.

The version on the build machine, and the
package behind it:

```
$ lsof -v 2>&1 | head -4
lsof version information:
    revision: 4.95.0
    latest revision: https://github.com/lsof-org/lsof
    latest FAQ: https://github.com/lsof-org/lsof/blob/master/00FAQ
$ dpkg -l lsof | tail -1
ii  lsof           4.95.0-1build3 amd64        utility to list open files
```

Run with no arguments, lsof prints *every*
open file of *every* process it can see. On
the build machine that answer is not short:

```
$ lsof | wc -l
3934
```

Nearly four thousand rows on an idle-ish
machine — which is why nobody reads lsof
bare. The whole craft is in the *selection*:
naming the file, the process, the user, or
the port you care about and letting
everything else fall away. The selections
are the next ten chapters; this one plants
something to select.

## The first plant

The lab's simplest holder is a `tail -f`
following a small log file — the classic
"a process is watching this file" specimen:

```
$ tail -f tree/notes.log &   [started pid 22329]
```

Now ask the first question. Give lsof the
file's name, and it answers with the holder:

```
$ lsof /home/hatch/workspace/lsof-lab/tree/notes.log
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
tail    22329 root    3r   REG   0,86       23 7484136 /home/hatch/workspace/lsof-lab/tree/notes.log
[exit 0]
```

One row. Read it left to right, because every
row in the guide has this shape:

| Column | This row | Meaning |
| --- | --- | --- |
| COMMAND | `tail` | the program's name (truncated to 9 characters) |
| PID | `22329` | the process ID — the lab planted it, so this is checkable |
| USER | `root` | whose process it is |
| FD | `3r` | file descriptor 3, opened for **r**eading — chapter 2 decodes this column fully |
| TYPE | `REG` | a regular file (directories are `DIR`, sockets `IPv4`/`IPv6`, and more) |
| DEVICE | `0,86` | major,minor numbers of the filesystem holding it |
| SIZE/OFF | `23` | for a regular file, its size in bytes — the log really is 23 bytes |
| NODE | `7484136` | the file's inode number |
| NAME | the path | what the handle points at |

Check: the pid in the row is the pid the
shell reported when the plant started, the
size matches the two short lines written
into the log, and no other process appears —
nothing else on the machine had that file
open. That is the basic move of the whole
guide: **plant a known state, ask lsof, and
grade its answer against what you planted.**

Two habits to start now. First, lsof prints
the path in NAME exactly as the kernel knows
it — usually absolute, as here, even though
the lab asked with an absolute path too;
chapter 3 looks at what name arguments
actually match. Second, lsof's silence is
information with an exit code attached: ask
about a file nobody holds and you get no
rows and exit 1 (chapter 7 captures it).
An empty answer is an answer.

Next: the same `tail`, asked by pid instead
of by file — its whole table, and the FD
column taken apart letter by letter.
