# Glossary

**Access letter** — the letter bolted onto a
numbered FD in lsof's output: `r` read, `w`
write, `u` both. Named descriptors (cwd,
txt…) carry no letter. Chapter 2.

**a_inode** — lsof's TYPE for anonymous
inode handles: kernel channels with no file
behind them. The lab met `inotify` — the
change-notification handle `tail -f` holds.
Chapters 2, 10.

**CHR** — TYPE for a character device:
terminals, `/dev/null`, and kin. Chapter 2.

**cwd** — a process's current working
directory, held as a named descriptor. A
process standing in a directory is one of
the things keeping that directory "busy."
Chapters 2, 3, 9.

**Deleted but open** — a file whose last
directory entry was removed while a process
still holds it. Invisible to `ls`/`du`,
still charged to the filesystem by `df`,
findable with `lsof +L1`, freed only when
the last holder closes it. Chapter 4.

**Descriptor** — see *file descriptor*.

**DEVICE** — the major,minor numbers of the
filesystem (or device) a handle belongs to.
Mostly a cross-check column; on sockets it
holds the socket's inode instead. Chapters
1, 5.

**-d selection** — lsof's descriptor-set
filter: `lsof -a -p PID -d cwd` prints only
cwd rows. Items can be negated with `^`
(`-d ^mem,^cwd`). Chapters 2, 6, 9.

**ESTABLISHED** — a TCP state: the
connection is open and passing (or able to
pass) data. Sockets carry states in the
NAME column's parentheses. Chapter 5.

**FD** — the file-descriptor column: named
descriptors (cwd, rtd, txt, mem), then the
numbered handles with access letters.
Chapter 2.

**Field output (-F)** — lsof's
machine-readable form: one field per item,
introduced by a one-letter tag, NUL-
separated under `-F0`. The only output a
script should parse. Chapter 7.

**File descriptor** — the numbered handle a
process holds on a file, directory, device,
pipe, or socket. Numbered from 0; 0, 1, 2
are the standard streams. Chapter 2.

**fuser** — the blunt neighbour: names (or,
with `-k`, kills) the processes using a
file or socket, in pids and terse access
letters. Chapter 10.

**Holder** — this guide's word for a process
with a given file, directory, or socket
open. "Who holds this?" is the lsof
question. Throughout.

**inode** — a filesystem's internal record
for a file: its identity, independent of
any name. lsof's NODE column; two names for
one inode are the same file. Chapter 1.

**Link count / NLINK** — how many directory
entries point at an inode. Zero with the
file still open is the deleted-but-open
state; `+L1` selects link counts below 1.
Chapter 4.

**LISTEN** — a TCP state: a socket bound to
a port and accepting connections. UDP has
no states. Chapter 5.

**mem** — the named descriptor for files
mapped into a process's memory — its shared
libraries, mostly. Chapter 2.

**NAME** — the rightmost column: the path,
address pair, or kernel object a handle
points at. Deleted files are tagged
`(deleted)` here. Chapter 1.

**NOFD** — the line lsof prints in place of
a descriptor table it was not permitted to
read: "no file descriptors" *visible*, not
none existing. Chapter 8.

**OR / AND selections** — lsof combines
different selection types with OR by
default; `-a` makes them AND. Commas inside
one selection are a list (OR), `^` negates
an item. Chapter 6.

**+D** — the recursive directory search:
every open file under a directory tree.
Powerful, slow, and its exit code is not a
verdict. Chapters 3, 7.

**+L1** — the link-count search at "less
than 1": every open file with no name left —
the deleted-but-open audit. Chapters 4, 7.

**/proc/<pid>/fd** — the raw descriptor
table: one symlink per handle, the evidence
lsof itself reads. Chapter 10.

**rtd** — a process's root directory: `/`,
unless the process is chrooted. Chapter 2.

**Skeleton row** — a row for a process the
kernel won't let you inspect: TYPE
`unknown`, `readlink: Permission denied` in
NAME, usually with a `NOFD` line. Chapter 8.

**SIZE/OFF** — for a regular file, its size
in bytes; for sockets and devices, an
offset-style counter (`0t0`) that is not a
size. Chapters 1, 2.

**ss** — the socket-native neighbour: asks
the kernel's socket tables directly; states,
queues, timers. Chapters 5, 10.

**txt** — the named descriptor for the
program file itself: which binary a process
is. Chapter 2.

**TYPE** — what kind of thing a handle is:
`REG` file, `DIR` directory, `CHR` device,
`IPv4`/`IPv6` socket, `a_inode` kernel
channel, `FIFO` pipe, `unknown` (withheld).
Chapter 2.
