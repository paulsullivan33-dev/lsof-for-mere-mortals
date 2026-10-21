# Scripting with lsof

**Scope:** lsof as a data source — the `-F`
field output built for parsers, a shipped
script that walks it, exit codes (dependable
for plain selections, not for the search
modes, with the captures to prove both), and
`-r`, lsof's own repeating snapshot.

## Output meant for machines: -F

The nine-column table is aligned for eyes,
which makes it treacherous for scripts: a
filename with a space in it is
indistinguishable from two columns. `-F`
switches lsof to **field output** — one
field per item, each introduced by a
one-letter tag (`p` pid, `c` command, `f`
descriptor, `n` name, and more). With `-F0`
the separator is a NUL byte instead of a
newline, so no filename, however hostile,
can break the framing. The lab's holder
under `-Fpcfn`, NULs turned back into lines
by `tr` for the page:

```
$ lsof -Fpcfn -p 22472 | tr '\0' '\n' | head -24
p22472
cpython3
fcwd
n/home/hatch/workspace/lsof-lab
frtd
n/
ftxt
n/usr/bin/python3.12
fmem
n/usr/lib/locale/C.utf8/LC_CTYPE
...
f0
n/dev/null
```

The rhythm is mechanical: a `p` opens a
process, an `f` opens a descriptor, the `n`
after it is that descriptor's name. The
shipped `examples/open-files.sh` walks
exactly that rhythm with `awk` and prints a
script-friendly table:

```
$ /home/hatch/workspace/lsof-for-mere-mortals/examples/open-files.sh 22472
22472 cwd /home/hatch/workspace/lsof-lab
22472 rtd /
22472 txt /usr/bin/python3.12
22472 mem /usr/lib/locale/C.utf8/LC_CTYPE
...
22472 3 /home/hatch/workspace/lsof-lab/tree/script.txt
22472 4 /home/hatch/workspace/lsof-lab/tree/both.txt
[exit 0]
```

Fifteen lines for the holder, the two
planted files last — the same table as
chapter 2, flattened for a pipeline. If you
script lsof, script this output, not the
pretty one.

## Exit codes: where they hold

For **plain selections**, lsof's exit code
is a clean boolean — 0 found, 1 not found —
and the lab has it from several directions:

```
$ lsof -p 999999
[exit 1]
$ lsof /home/hatch/workspace/lsof-lab/tree/unopened.txt
[exit 1]
```

A pid that doesn't exist; a file that exists
but nobody holds (planted for the purpose,
with content in it — an unopened file is
invisible to lsof no matter how real it is).
Chapter 5's dead port and chapter 6's
empty AND agree: exit 1, no rows. A script
may lean on that.

## Where they don't: +D and +L

The search modes break the contract, and
the lab measured it rather than assuming.
With a `tail` planted on a lab file, three
consecutive `+D` runs over the lab tree —
the same tree chapter 3 showed returning
all three holders — all reported failure:

```
$ lsof +D /home/hatch/workspace/lsof-lab/tree (run 1)
[exit 1]
$ lsof +D /home/hatch/workspace/lsof-lab/tree (run 2)
[exit 1]
$ lsof +D /home/hatch/workspace/lsof-lab/tree (run 3)
[exit 1]
$ lsof +L1
[exit 0]
```

…and the `+L1` that closed the session,
run when nothing on the machine held a
deleted file, printed nothing and exited
**0**. Under `+D`/`+L`, the exit status is
entangled with the internal search (files
that vanish mid-scan, entries it cannot
process) rather than with "did you find
any" — in this lab it pointed the wrong way
in both directions. The rule for scripts:
after a plain selection, trust `$?`; after
`+D` or `+L`, **test the output** (non-empty?
the row you expected?) and treat the code as
noise. Chapter 3's `+D` exhibit — right
rows, exit 1 — is the same lesson from the
other side.

## Watching it change: -r

`-r N` repeats the query every N seconds,
separating snapshots with a `=======` line —
lsof's own watch mode, no `watch` wrapper
needed. The lab let one run against the
planted listener under a 3-second `timeout`:

```
$ timeout 3 lsof -r 2 -i :8734
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22473 root    3u  IPv4 859403      0t0  TCP localhost:8734 (LISTEN)
python3 22473 root    4u  IPv4 859404      0t0  UDP localhost:8734 
=======
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22473 root    3u  IPv4 859403      0t0  TCP localhost:8734 (LISTEN)
python3 22473 root    4u  IPv4 859404      0t0  UDP localhost:8734 
=======
[exit 124]
```

Two snapshots two seconds apart, identical
(this listener's life is uneventful), and
the 124 at the end is `timeout`'s exit, not
lsof's — `lsof -r` runs forever until
killed, which under `timeout` is the normal
way to take a bounded sample. In an
incident, `-r` on a port or pid is how you
catch the connection that only exists for a
moment.
