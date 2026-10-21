# Troubleshooting

**Scope:** lsof's failure shapes, each met
in the lab: silence, skeletons, warnings,
slowness, misleading exit codes — and the
one failure that isn't lsof's: acting on a
row you didn't finish reading.

## "It printed nothing"

Silence plus exit 1 is lsof's "no," and it
has three ordinary causes, all captured:

- **Nobody holds it.** A file that exists
  but is unopened is invisible to lsof
  (chapter 7's planted `unopened.txt`,
  content and all, exit 1). lsof is not a
  file finder — that's the sibling *Finding
  Files* guide; lsof finds files *in use*.
- **Nothing is on that port / that pid
  doesn't exist.** Chapter 5's after-kill
  check and chapter 7's `lsof -p 999999`:
  same silence, same code. In a script, for
  plain selections, that's a dependable
  signal.
- **Somebody holds it — somebody else.**
  Chapter 8: the file root held was a blank
  to the specimen user, exit 1. Silence from
  a non-root account proves "not by anyone
  *you may see*," which is a smaller claim.

And the fourth cause, from chapter 6: the
selection logic, not the system — an `-a`
intersection that is legitimately empty, or
an OR missing its `-a` drowning the answer
in rows you scroll past. If lsof's answer
looks wrong in either direction, re-read
the command before doubting the machine.

## "The rows are skeletons"

`unknown` in TYPE, `readlink: Permission
denied` in NAME, and a `NOFD` line where
the descriptors should be: you are looking
at a process whose owner you are not
(chapter 8, from the specimen side). The
process is real; its contents are withheld
by the kernel, not lost by lsof. Root
doesn't see skeletons on a stock system —
and if root *does* (the build sandbox's
compartments did it), the machine is
telling you its root is fenced, which is
its own useful fact.

Relatedly: `NOFD` is not "the process has
no open files." It is "you may not look."
Processes always have files open.

## "can't stat() … may be incomplete"

The chapter 8 warning:

```
lsof: WARNING: can't stat() tmpfs file system /home/hatch/.pki/nssdb
      Output information may be incomplete.
```

lsof stats every mounted filesystem to map
devices; one it cannot stat (another user's
mount, a fuse filesystem with tight
permissions) earns the warning and a gap in
the map. Treat output under this warning as
*correct but possibly incomplete*: a missing
row is not proof of absence while the
warning stands. Running as root usually
clears it; on multi-user machines it can be
a permanent companion, and scripts should
expect lsof's answers on stderr to exist.

## "It's so slow"

Profile before blaming: a bare `lsof` on
the lab machine printed 3,934 rows and a
full `+D /usr` took 2.8 seconds where an
exact-file question took 0.023 (chapters 1
and 3). The costs, in order:

- **`+D` on a big tree** — it walks the
  whole tree first. Shrink the tree.
- **A bare run** on a busy server — tens of
  thousands of rows and every process's
  memory maps. Select something.
- **Name resolution** — `localhost` in the
  NAME column means lsof is consulting DNS
  and `/etc/services` per row. `-n -P` turns
  both off and is the single biggest
  speed-up for wide queries.

## "The exit code lied"

Chapter 7's measured rule, restated: plain
selections (a name, `-p`, `-i`, `-u`, `-c`)
— 0 found, 1 not found, trustworthy. The
`+D`/`+L` search modes — the code tracks
the search's internal errors, not your
question; the lab captured correct rows
with exit 1 and an empty result with exit
0. Scripts that must use the search modes
should test output, not `$?`.

## "I killed it and something else broke"

The failure that isn't lsof's. Rows give
pids, and pids get reused, get misread, and
belong to things with users. The lab's
discipline transfers directly: before
acting on a holder, name it fully
(`ps -p PID -o args=` — the sibling
*Watching Your System* guide), prefer the
service's own controls (restart, reload,
logrotate's reopen) over a kill, and treat
`fuser -k` (chapter 10) as what it is — a
pre-aimed SIGKILL at *every* match. When
the holder is a database or a queue worker,
"the space came back" can be the most
expensive sentence in the incident report.

## Exit-code field guide

| Situation | Rows | Exit |
| --- | --- | --- |
| File held, plain question | the holders | 0 |
| File unopened / pid absent / port free | none | 1 |
| AND selection, empty intersection | none | 1 |
| `+D`, rows found | the rows | 1 in every lab capture |
| `+L1`, rows found | the rows | 0 in the lab capture |
| `+L1`, nothing held-deleted | none | 0 in the lab capture |
| Another user's process, by pid | skeleton + `NOFD` | 0 |
| Another user's file | none | 1 |

The middle rows are the anomaly, captured
in sessions s04, s05, and s11 — the table
reports the lab, and your machine agreeing
or not is itself worth knowing.
