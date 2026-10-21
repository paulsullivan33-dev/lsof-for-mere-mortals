# lsof for Mere Mortals

Some questions about a running system have
no answer in a file listing. A disk is full
and `du` swears nothing is using the space.
A service won't start because "the port is
already in use," by whom it won't say. A log
file keeps growing after you deleted it.
Each of these is a question about **open
files** — not files at rest on the disk, but
files in use, held by processes, right now —
and the tool that answers them is **lsof**,
"list open files."

On Linux almost everything a process touches
is presented as a file: documents and logs,
yes, but also its working directory, the
program binary itself, its libraries, its
terminals and pipes, and every network
socket. So one table — which process holds
what, and how — answers an outsized share of
"why is the system doing that" questions.
The sibling guide *Watching Your System for
Mere Mortals* covers `ps` and `top`, which
say what a process is and how hard it's
working; this guide starts there and asks
the next question: **what is it holding?**

lsof's output looks forbidding — nine
columns of codes — and its selection rules
hide one genuine trap (selections *add up*
unless you tell them not to; chapter 6 fell
into it on purpose, in the lab, so you can
watch it happen). This guide decodes the
table on processes planted to be found,
walks the deleted-but-open classic end to
end with the disk numbers moving on the
record, and checks lsof's answers against
its neighbours — `ss`, `fuser`, and the raw
`/proc` filesystem it reads.

The lab is a set of small planted processes:
a `tail -f` on a log, a Python holder script
and a socket listener (both shipped in
`examples/`), a sleeper with its working
directory planted in a corner of the tree,
and — for one chapter — a scratch user,
created and removed on the record. Every
claim in the guide is proven by an
observable state change: a port's row
present, then gone; a `df` total that only
moves when the right process dies.

A note on how this guide was verified. lsof
**4.95.0** (the Ubuntu build,
`4.95.0-1build3`) was on the build machine,
and every command quoted was run against
the lab and captured. PIDs, inode numbers,
and timings in the captures are the capture
runs' own and will differ on yours; the
shapes of the answers won't. Where a
reader's machine behaves differently — a
stock system where root sees more than this
guide's sandbox let it see, NFS mounts,
macOS — the chapters say so in place and
`criteria.md` keeps the ledger of what is
documented-only.

## What this guide covers

- [**What lsof is**](what-lsof-is.md) —
  open files as the system's common
  currency; the three questions lsof
  answers; your version; the first planted
  holder, found from its file alone
- [**Reading a process**](reading-a-process.md) —
  one process's whole table: the FD column
  decoded (cwd, rtd, txt, mem, the numbered
  handles and their r/w/u letters), the
  TYPE column, and slicing the table with
  `-d`
- [**Who has this file**](who-has-this-file.md) —
  asking by name: one file exactly, a
  directory (which is not its contents),
  and `+D`, the recursive search — priced
  in seconds
- [**Deleted but open**](deleted-but-open.md) —
  the centerpiece: a 200 MiB file deleted
  under its holder, `df` and `du` parting
  company, `+L1` naming the holder, and the
  space coming back only when it dies
- [**Ports and sockets**](ports-and-sockets.md) —
  `-i`, listeners and the stateless UDP
  rows, an established connection seen from
  both ends, and the same answers
  cross-checked with `ss` until the
  listener is stopped and both go quiet
- [**Combining selections**](combining-selections.md) —
  the OR rule, `-a` for AND, pid lists and
  `^` exclusions, `-c` by command name —
  including the lab's own `-d` trap
- [**Scripting with lsof**](scripting-with-lsof.md) —
  `-F` field output and a parsing script,
  exit codes (and where they stop being
  trustworthy), and `-r`, the repeating
  snapshot
- [**Whose eyes**](whose-eyes.md) — root
  versus a normal user: full tables, skeleton
  rows, the `NOFD` line, and the
  `can't stat()` warning, all captured
- [**Recipes**](recipes.md) — the everyday
  set: the port hog, the full-disk audit,
  who is standing in this directory, a
  daemon's open set, who writes this log
- [**The neighbours**](the-neighbours.md) —
  `fuser` (including the loaded `-k`), the
  raw evidence in `/proc/<pid>/fd`, `ss`
  revisited, and the legacy of `netstat`
- [**Troubleshooting**](troubleshooting.md) —
  silence and what it means, skeleton rows,
  warnings, the slow search, and killing
  the right thing
- [**Glossary**](glossary.md) — the terms,
  collected in one place

## What it doesn't cover

What processes are and how loaded the
machine is — the sibling *Watching Your
System for Mere Mortals* owns `ps`, `top`,
and `htop`. Locating files at rest by name,
size, or age is *Finding Files for Mere
Mortals*; this guide locates files *in
use*, including the one kind `find` cannot
see at all. Making connections to inspect
is *Netcat for Mere Mortals'* territory; the
lab's sockets are loopback specimens. NFS
behaviour, and the macOS and BSD dialects
of lsof, are named where they differ and
labelled documented-only — the lab is one
Linux machine. Kernel-level tracing of
*why* a process opened something belongs to
tools this series hasn't covered; lsof
reports the state, not the story.

## How to use this guide

Read chapters 1–3 in order; they install
the table, the FD column, and the asking-by-
name habit everything else stands on. After
that, chapters stand alone — chapter 4 is
the one to open when a disk is full and
nothing accounts for it. The lab plants are
tiny and self-cleaning: two scripts in
`examples/` (`hold.py`, `listen.py`) and a
`tail` or `sleep` you start and stop
yourself. Practise on those before pointing
lsof at a production incident; the commands
are the same, and the calm is transferable.
