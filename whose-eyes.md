# Whose Eyes

**Scope:** the same machine seen by two
users — root's view and a normal user's —
captured with a scratch account created and
removed on the record. What a non-root user
sees fully (their own processes), what they
see as a skeleton (everyone else's), and the
warnings that ride along.

## Why this chapter exists

Every capture so far was made as **root**,
and root's lsof is the full table for every
user. That is not the lsof most people meet.
A normal user gets complete answers about
*their own* processes — and something much
thinner about everyone else's, because the
information lives in `/proc/<pid>/`, and the
kernel only lets a process's owner (and
root) read its descriptor links. The lab
built the second pair of eyes: a scratch
user, `specimen`, plus two planted holders —
root holding `/tmp/roothold.txt` (pid
24210), specimen running a `sleep` and a
`tail -f` on its own file:

```
$ useradd -m -s /bin/bash specimen
[exit 0]
[planted: root holder pid 24210 on /tmp/roothold.txt; specimen's sleep pid 24214; specimen's tail pid 24220 on /tmp/specimen.log]
```

## The user's own table: complete

Asked by specimen about specimen's file, the
answer is whole and exact:

```
$ su specimen -c 'lsof /tmp/specimen.log'
...
COMMAND   PID     USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
tail    24220 specimen    3r   REG   0,79       18  289 /tmp/specimen.log
[exit 0]
```

And `lsof -p 24220` *as specimen* prints
that tail's entire table — cwd, libraries,
descriptors, the lot (kept whole in the
transcripts) — identical in completeness to
anything root saw in earlier chapters. Your
own processes are fully yours to inspect;
no sudo needed for the questions most people
actually ask lsof.

## Everyone else's: the skeleton

Asked by specimen about root's planted file,
the answer is silence and exit 1 — root's
holder is simply not visible through that
door. Asked directly about root's pid, lsof
shows the shape of the limit:

```
$ su specimen -c 'lsof -p 24210'
...
COMMAND   PID USER   FD      TYPE DEVICE SIZE/OFF NODE NAME
python3 24210 root  cwd   unknown                      /proc/24210/cwd (readlink: Permission denied)
python3 24210 root  rtd   unknown                      /proc/24210/root (readlink: Permission denied)
python3 24210 root  txt   unknown                      /proc/24210/exe (readlink: Permission denied)
python3 24210 root NOFD                                /proc/24210/fd (opendir: Permission denied)
[exit 0]
```

This is the **skeleton row** pattern, worth
learning to recognise: the process exists
(command, pid, user — from data anyone may
read), its named links refuse
(`readlink: Permission denied`, TYPE demoted
to `unknown`), and a single **NOFD** line
stands where its descriptor table would be:
lsof could not even open `/proc/24210/fd`.
Note the exit code is 0 — lsof *did* report
the process; skeleton output is a successful
answer with the contents withheld. A
full bare run as specimen is skeletons all
the way down for other users' processes
(the transcripts keep the head of one; the
column headers even grow `TID`/`TASKCMD`
columns in that view).

## The warning that rides along

Every one of specimen's runs above was
preceded on stderr by:

```
lsof: WARNING: can't stat() tmpfs file system /home/hatch/.pki/nssdb
      Output information may be incomplete.
lsof: WARNING: can't stat() squashfs file system /home/hatch/assets
      Output information may be incomplete.
```

(Each printed twice in the raw capture —
once per pass lsof makes; the chapter shows
one pair.) lsof stats every mounted
filesystem to build its device table; a
filesystem the *user* cannot stat — here,
two mounts belonging to the build sandbox's
own machinery — produces this warning and a
possibly incomplete device map. Root's runs
never showed it, because root can stat
these. On a reader's machine the names will
be different (a fuse mount, another user's
tmpfs), the meaning the same: **some
filesystem was skipped; rows depending on it
may be missing.** It's a warning, not a
failure — the answers it did give above are
correct as far as they go.

## The build sandbox's confession

One artefact of the lab's environment, stated
plainly because the transcripts show it:
when *root* listed specimen's processes
(`lsof -u specimen` — the `-u` selection,
working as advertised), this sandbox's root
also got skeleton rows for them:

```
$ lsof -u specimen
COMMAND   PID     USER   FD      TYPE DEVICE SIZE/OFF NODE NAME
sleep   24214 specimen  cwd   unknown                      /proc/24214/cwd (readlink: Permission denied)
...
tail    24220 specimen    3   unknown                      /proc/24220/fd/3 (readlink: Permission denied)
[exit 0]
```

The build machine confines its root inside
a sandbox, and the `su`-started processes
live in a neighbouring compartment whose
`/proc` links even this root may not read.
On a stock Linux system, root's lsof shows
the **full** table for every user — the
skeleton treatment is what the kernel gives
*non-owners*, and this sandbox extends it
to its own root across compartments. The
shapes are what transfer: full table for
your own, skeleton plus `NOFD` for processes
whose owner-or-compartment you are not, and
silence when you ask about a file only they
hold.

## Cleanup, on the record

The scratch user was a specimen, not a
resident:

```
$ userdel -r specimen
userdel: specimen mail spool (/var/mail/specimen) not found
[exit 0]
$ id specimen
id: 'specimen': no such user
[exit 1]
```

(The mail-spool line is `userdel` noting
there was no spool to remove.) Its processes
were killed first, its planted files
removed — the lab machine ends the chapter
with exactly the accounts it started with.
