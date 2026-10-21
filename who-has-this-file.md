# Who Has This File

**Scope:** asking by name — a file's holders
exactly, the surprise in asking about a
*directory*, and `+D`, the recursive search
that answers the question you probably meant,
priced honestly against the exact question.

## One file, exactly

Chapter 1's move is the everyday one: hand
lsof a filename and it prints the rows whose
NAME matches, from every process on the
machine:

```
$ lsof /home/hatch/workspace/lsof-lab/tree/top.log
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
tail    22373 root    3r   REG   0,86        4 7484169 /home/hatch/workspace/lsof-lab/tree/top.log
[exit 0]
```

The planted `tail` (pid 22373), and nobody
else. Note that lsof matched the file by its
identity, not by the string: ask with a
different spelling of the same path (a
symlink, a `..` detour) and the row still
comes back, because lsof stats the name you
give it and searches for that inode.

## A directory is not its contents

Now the trap. The lab plants three holders
in one tree — `tail` on `tree/top.log`, the
holder script on `tree/sub/deep.txt`, and
the chapter 2 sleeper standing in
`tree/sub`:

```
[planted: tail pid 22373 on tree/top.log; holder pid 22374 on tree/sub/deep.txt; sleeper pid 22375 with cwd tree/sub]
```

Ask about the directory `tree/sub` the same
way, and a reasonable person expects both
the sleeper *and* the holder of the file
inside it. lsof answers more literally:

```
$ lsof /home/hatch/workspace/lsof-lab/tree/sub
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
sleep   22375 root  cwd    DIR   0,86       16 7484148 /home/hatch/workspace/lsof-lab/tree/sub
[exit 0]
```

Only the sleeper — because only the sleeper
holds *the directory itself* open (as its
cwd). The holder of `deep.txt` holds the
file, not its parent. A name argument to
lsof is an exact question, and "processes
using this directory" and "processes using
files under this directory" are different
questions with different answers.

## +D: the recursive question

The second question has its own flag. `+D`
takes a directory and searches it
**recursively** — every file under it,
matched against every process's open set:

```
$ lsof +D /home/hatch/workspace/lsof-lab/tree
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF    NODE NAME
tail    22373 root    3r   REG   0,86        4 7484169 /home/hatch/workspace/lsof-lab/tree/top.log
python3 22374 root    3r   REG   0,86        5 7484170 /home/hatch/workspace/lsof-lab/tree/sub/deep.txt
sleep   22375 root  cwd    DIR   0,86       16 7484148 /home/hatch/workspace/lsof-lab/tree/sub
[exit 1]
```

All three plants, at both depths. This is
the command behind "something is using files
in this tree — what?" — the question you ask
before unmounting a filesystem or deleting a
directory that insists it's busy.

Two honest warnings, both visible in the
capture. First, the exit code: the answer is
complete and correct, and lsof still exited
**1**. Under the search options `+D` and
`+L`, the exit status does not track "found
it" the way it does for plain selections —
chapter 7 lines the evidence up. Read the
rows; don't grade `+D` by its `$?`.

Second, the price. `+D` has to walk the
whole tree collecting inodes, *then* scan
every process. The same capture session
timed both questions:

```
$ time lsof +D /usr > /dev/null

real	0m2.807s
$ time lsof /home/hatch/workspace/lsof-lab/tree/top.log > /dev/null

real	0m0.023s
```

Seconds against hundredths — and `/usr` is
not a large tree by server standards. On a
big filesystem, `+D /` can take minutes and
noticeable CPU. The discipline: ask the
exact question (a file, a pid, a port)
whenever you can, and reserve `+D` for the
smallest directory that could contain the
answer.

One cost is documented rather than captured:
on an NFS mount whose server has stopped
answering, lsof itself can block while it
stats files there — the search inherits the
mount's health. No NFS mount exists on the
build machine, so the guide states the
behaviour without a capture; `criteria.md`
logs it as documented-only.

Check: given a tree with known holders, you
can now produce each holder with the right
question — exact name for the file, the
directory itself for who is *standing* in
it, `+D` for everything beneath it — and
you know which of the three costs real time.
