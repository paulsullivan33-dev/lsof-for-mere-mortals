# Reading a Process

**Scope:** one process's complete lsof
table, row by row — the named descriptors
(cwd, rtd, txt, mem), the numbered ones and
their access letters, the TYPE column — and
how to slice the table down to one kind of
row with `-d`.

## The whole table for one pid

Ask lsof about a process instead of a file
and it prints everything that process holds.
The chapter 1 `tail`, by pid:

```
$ lsof -p 22329
COMMAND   PID USER   FD      TYPE DEVICE SIZE/OFF                NODE NAME
tail    22329 root  cwd       DIR   0,86       72             7483797 /home/hatch/workspace/lsof-lab
tail    22329 root  rtd       DIR   0,42       32 9223372036854776064 /
tail    22329 root  txt       REG   0,42    64032 9223372036854779370 /usr/bin/tail
tail    22329 root  mem       REG   0,42  2129424 9223372036854835899 /usr/lib/x86_64-linux-gnu/libc.so.6
tail    22329 root  mem       REG   0,42   236616 9223372036854835482 /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
tail    22329 root    0r      CHR    1,3      0t0                   4 /dev/null
tail    22329 root    1w      REG   0,86      623             7484135 /home/hatch/workspace/lsof-lab/transcripts/s01-first-look.txt
tail    22329 root    2w      REG   0,86      623             7484135 /home/hatch/workspace/lsof-lab/transcripts/s01-first-look.txt
tail    22329 root    3r      REG   0,86       23             7484136 /home/hatch/workspace/lsof-lab/tree/notes.log
tail    22329 root    4r  a_inode   0,17        0                  59 inotify
[exit 0]
```

The FD column has two populations. The
**named** descriptors come first, and every
process has them:

- **cwd** — the process's current working
  directory. Here, the lab root: the shell
  started `tail` there. A process's cwd is a
  real hold on that directory — remember it
  when a directory refuses to be removed.
- **rtd** — its root directory, `/` for
  almost everything (a chrooted process
  would show its jail here instead).
- **txt** — the program file itself, the
  executable being run: `/usr/bin/tail`,
  64,032 bytes. This is how you answer "that
  process named `python3` — *which* python,
  running *what* binary?" when the command
  line is too vague.
- **mem** — files mapped into memory,
  typically the shared libraries the program
  loaded: the C library and the dynamic
  loader here. Long-lived processes collect
  many mem rows; they're usually the least
  interesting part of a table, and the first
  thing to filter out when skimming.

Then the **numbered** descriptors — the ones
the process itself opened, each numbered as
the process knows it, with an access letter
bolted on:

- `0r` — descriptor 0 (standard input), read:
  `/dev/null`, TYPE `CHR` (a character
  device). The lab's plants were started with
  input from nowhere.
- `1w` and `2w` — standard output and
  standard error, write: both point at the
  transcript file this capture was being
  written into. lsof is cheerfully
  self-referential — it will show you the
  capture watching itself.
- `3r` — the planted file, the row chapter 1
  found by name.
- `4r` — a surprise worth the row: TYPE
  `a_inode`, NAME `inotify`. `tail -f` on a
  modern system doesn't poll the file; it
  asks the kernel to notify it of changes,
  and that notification channel is itself a
  handle. Tools hold more than they open on
  purpose.

## The access letters, all three

The lab's holder script (`examples/hold.py`)
exists to make the letters unambiguous — it
opens what you tell it, in the mode you tell
it, and sleeps. Four opens, four rows:

```
$ python3 bin/hold.py tree/read.txt:r tree/write.txt:w tree/both.txt:u tree/sub:d &   [started pid 22347]
$ lsof -p 22347
...
python3 22347 root    3r   REG   0,86        8             7484149 /home/hatch/workspace/lsof-lab/tree/read.txt
python3 22347 root    4w   REG   0,86        0             7484151 /home/hatch/workspace/lsof-lab/tree/write.txt
python3 22347 root    5u   REG   0,86       10             7484150 /home/hatch/workspace/lsof-lab/tree/both.txt
python3 22347 root    6r   DIR   0,86        0             7484148 /home/hatch/workspace/lsof-lab/tree/sub
[exit 0]
```

- **r** — read. `read.txt`, opened read-only.
- **w** — write. `write.txt` was created by
  the open itself; SIZE/OFF 0 because the
  holder never wrote a byte.
- **u** — read *and* write ("u" for the
  both-ways mode, from the Unix term). This
  is the letter most sockets and many daemon
  files wear.
- The fourth row is a **directory held open**
  as a numbered descriptor: TYPE `DIR`. A
  process can hold a directory the same way
  it holds a file — chapter 3's directory
  questions start here.

(The holder's cwd/rtd/txt/mem and 0/1/2 rows
are identical in shape to `tail`'s above and
elided; the full table is in the lab
transcripts.)

SIZE/OFF deserves its sentence: for a
regular file it's the file's size; for a
socket or device it's an offset-ish counter
printed as `0t0` — read it as "not a size"
rather than "zero".

## Slicing by descriptor: -d

A full table is often more than the question
needs. `-d` selects descriptor kinds, and a
planted sleeper shows it cleanly. This one
was started *inside* `tree/sub`, so its cwd
is the interesting row:

```
$ bash -c 'cd tree/sub && exec sleep 240' &   [started pid 22359]
$ lsof -a -p 22359 -d cwd
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
sleep   22359 root  cwd    DIR   0,86        0 7484148 /home/hatch/workspace/lsof-lab/tree/sub
[exit 0]
$ lsof -a -p 22359 -d txt
COMMAND   PID USER  FD   TYPE DEVICE SIZE/OFF                NODE NAME
sleep   22359 root txt    REG   0,42    35336 9223372036854779295 /usr/bin/sleep
[exit 0]
```

Two things to notice. First, the `-a` is
load-bearing: it makes the `-p` and `-d`
selections *both* apply (AND). Without it,
lsof would add the selections together (OR)
and print far more than this — chapter 6
demonstrates that with an exhibit. Second,
the answers cross-check against the raw
`/proc` filesystem lsof itself reads:

```
$ readlink /proc/22359/cwd
/home/hatch/workspace/lsof-lab/tree/sub
[exit 0]
$ readlink /proc/22359/exe
/usr/bin/sleep
[exit 0]
```

Same directory, same binary. lsof is a
reader and organiser of `/proc`, not a
separate source of truth — chapter 10 comes
back to the neighbours with that in mind.

Check: in any `-p` table you can now name
every row's kind, say which descriptors the
process opened itself, and read its access
modes off the letters. Next, the questions
turn around: not "what does this process
hold" but "who holds *this*."
