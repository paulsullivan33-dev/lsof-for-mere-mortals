# Deleted but Open

**Scope:** the classic lsof case, end to
end — a large file deleted while a process
holds it, the space that stays used though
no directory admits to it, the `+L1` search
that names the holder, and the recovery,
which happens only when the holder lets go.

## The setup: 200 MiB, planted and held

The lab creates a file of exactly
209,715,200 bytes (200 MiB) and records the
filesystem's state before anything happens:

```
$ fallocate -l 200M tree/big/big.bin
[exit 0]
$ ls -l tree/big/big.bin
-rw-rw---- 1 root nogroup 209715200 Oct 21 01:15 tree/big/big.bin
[exit 0]
$ df -B1 . | tail -1     (before: file present, nobody holding it)
/dev/mapper/rv 107355308032 6858235904 99764953088   7% /home/hatch
$ du -sb tree/big
209715200	tree/big
[exit 0]
```

Two witnesses agree: `df` says the
filesystem has 6,858,235,904 bytes used, and
`du` accounts for the file's full size in
the directory. Now the holder script opens
the file — and while it holds it, the file
is deleted:

```
$ python3 bin/hold.py tree/big/big.bin:r &   [started pid 22406]
$ rm tree/big/big.bin
[exit 0]
```

## The disagreement

```
$ df -B1 . | tail -1     (after rm: holder still has it open)
/dev/mapper/rv 107355308032 6858235904 99764953088   7% /home/hatch
$ du -sb tree/big
0	tree/big
[exit 0]
$ ls -l tree/big
total 0
[exit 0]
```

Read those three together, because this is
the exact shape of the classic incident:

- `ls` says the directory is empty. True.
- `du` says the directory uses 0 bytes.
  Also true — `du` walks directories, and no
  directory entry points at the file anymore.
- `df` says the filesystem's used total did
  not move **by a single byte**: 6,858,235,904
  before the delete, 6,858,235,904 after.

Both tools are telling the truth about
different things. Deleting a file removes
its *name*. The file's data blocks are freed
only when the name is gone **and** the last
open handle closes — and pid 22406 still has
the file open on descriptor 3. This is why
"we deleted the huge log but the disk is
still full" is not a mystery: some process
is still holding the log, usually the very
daemon that was writing it. It's also, in
reverse, a mercy: a process can keep using a
file that has been renamed away under it,
and log rotation schemes exploit exactly
this.

## Naming the holder: +L1

What you need is a search keyed on the
file's state, not its name — it has no name
anymore. `+L` selects by **link count**, and
`+L1` means "link count less than 1": files
with no directory entry left, still open:

```
$ lsof +L1
COMMAND   PID USER   FD   TYPE DEVICE  SIZE/OFF NLINK    NODE NAME
python3 22406 root    3r   REG   0,86 209715200     0 7484178 /home/hatch/workspace/lsof-lab/tree/big/big.bin (deleted)
[exit 0]
```

Everything the fix needs is in that row: the
process (pid 22406 — the planted holder, as
expected), the descriptor, the full size in
SIZE/OFF, the extra **NLINK** column `+L`
adds showing **0**, and the NAME wearing its
`(deleted)` tag. On a real incident the same
command lists every deleted-but-open file on
the machine, biggest suspects readable
straight off the SIZE/OFF column — this is
the full-disk audit, and the recipes
chapter keeps it as one.

(Scoped to one process, `lsof -a -p 22406
+L1` prints the same single row — the form
to use when you already suspect a pid.)

## The recovery: the holder lets go

There is no "close that file" command and
no way to reclaim the space from outside.
The space comes back when the process closes
the file or exits — in production that means
restarting (or signalling, for daemons that
reopen logs on `SIGHUP`) the holder you
identified. The lab just kills its plant:

```
$ kill 22406
$ df -B1 . | tail -1     (after the holder died: space given back)
/dev/mapper/rv 107355308032 6648580096 99956647936   7% /home/hatch
$ lsof +L1
[exit 0]
```

`df`'s used total fell by 209,655,808 bytes
— the file's 209,715,200, minus about 59 KB
of unrelated churn on a live filesystem
(the capture files themselves were being
written meanwhile). `+L1` now prints nothing:
no process on the machine holds a deleted
file open.

Two safety notes, plainly. First, identify
before you kill: the row gives you a pid,
not a verdict — look at what the process is
(the sibling *Watching Your System* guide's
`ps` work) before restarting a production
service over disk space; often a reload or
a `logrotate` signal is the intended door,
not a kill. Second, the reverse lesson:
deleting a file a process holds does not
disturb the process — which is why "delete
the evidence" cleanups fail against running
programs, and why a held-open deleted file
that *keeps growing* (check SIZE/OFF twice)
is itself a clue in an incident.

Check: `df` and `du` disagreeing by a large
round number is now a diagnosis, not a
puzzle — `lsof +L1` names the holder, and
the space returns when, and only when, the
holder closes or dies.
