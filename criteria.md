# Writing Criteria

Every guide in this repo is written to the same
standard. If you're adding or editing a guide —
human or AI — hold it to these.

1. **Plain words, real ideas.** Simple language,
   never dumbed-down concepts. Explain jargon on
   first use; collect terms in the glossary.
2. **No hype.** No marketing adjectives, no
   "revolutionary," no promises about what
   something will do for the reader.
3. **Honest about limits.** Say what the thing
   *can't* do. State uncertainty instead of
   smoothing it over. Validation notes include
   what remains unverified.
4. **No invented numbers.** Benchmarks, defaults,
   and specs are either measured or qualified with
   "depends on your setup." If it wasn't tested,
   say so.
5. **Checkable.** Commands are meant to be run,
   with "Check:" blocks showing what success looks
   like. Sources are linked, not asserted.
6. **Respect the reader's setup.** Call out
   Windows/Mac/Linux differences. Don't assume a
   GPU, a budget, or prior experience.
7. **Safety isn't skipped.** Real risks get
   stated plainly, not buried.
8. **Scoped.** Each guide says what it covers and
   points elsewhere for the rest. No guide
   pretends to be the whole subject.
9. **Structure over prose.** Tables, before/after
   examples, symptom → fix. Scannable beats essay.

## Verification notes for this guide

Standard 3 and 4 applied to this guide,
specifically. lsof **4.95.0** (the Ubuntu
package, `4.95.0-1build3`) was on the build
machine, and every quoted output is a
capture from it. Working transcripts are
kept with the build
(`lsof-lab/transcripts/`, fourteen capture
sessions, s01–s13 including the s07b and
s12/s13 supplements).

**The lab.** Planted processes only, each
started and killed inside its capture
session: a `tail -f` on planted logs; the
shipped `examples/hold.py` (Python 3.12.3),
which opens files in named modes (r/w/u,
and a directory via `os.open`) and sleeps;
the shipped `examples/listen.py`, holding a
TCP listener and a UDP socket on loopback
port 8734 and keeping accepted connections
open unanswered; a `sleep` with its cwd
planted in a tree corner; a 200 MiB
`fallocate` file; and a scratch user
`specimen`, created and deleted inside
session s09. The examples' `hold.py` and
`listen.py` are byte-identical to the lab
binaries that produced the captures (copied,
then diffed). Ports and pids quoted are the
captures' own.

**Verified by running, per chapter:**

- *Ch. 1:* `lsof -v` (revision 4.95.0), the
  dpkg line, the bare run's row count
  (3,934 lines at capture time), and a
  planted `tail -f` found from its file
  alone — pid 22329, `3r`, size 23 matching
  the planted log's two lines.
- *Ch. 2:* the full `-p` tables of that
  tail and of a holder with four planted
  opens — `3r` read, `4w` write (SIZE/OFF 0,
  nothing written), `5u` both ways, `6r` a
  directory — plus tail's `4r a_inode`
  inotify row. The sleeper's cwd and txt
  sliced out with `lsof -a -p … -d cwd|txt`
  and cross-checked against
  `readlink /proc/PID/cwd` and `…/exe`.
- *Ch. 3:* three holders in one tree: the
  exact file (one row), the directory as a
  plain argument (only the cwd row — the
  file inside it was **not** matched), and
  `+D` (all three rows, exit 1 despite the
  complete answer). Timings from the same
  session: `+D /usr` 2.807 s against 0.023 s
  for the exact file.
- *Ch. 4:* the centerpiece, in one session:
  `fallocate -l 200M` (209,715,200 bytes);
  `df -B1` used 6,858,235,904 before the
  delete and **identical to the byte** after
  `rm`, while `du -sb` went 209,715,200 → 0
  and `ls` showed an empty directory;
  `lsof +L1` named the holder (pid 22406,
  NLINK 0, `(deleted)`, SIZE/OFF
  209,715,200); after the holder was
  killed, `df` used fell to 6,648,580,096 —
  209,655,808 bytes returned, the file's
  size less ~59 KB of unrelated churn on a
  live filesystem — and `+L1` printed
  nothing.
- *Ch. 5:* the listener's rows (`-i :8734`,
  `-iTCP:8734 -sTCP:LISTEN`, `-iUDP:8734`);
  an ESTABLISHED pair from both ends with
  a hanging `curl` client; the same pids
  and fds in `ss -ltnp`/`-lunp`/`-tnp`,
  including ss's `Recv-Q 77` (the client's
  unread request bytes); timings `ss -tln`
  0.002 s vs `lsof -i` 0.009 s on this
  machine; after the kill, lsof exit 1 and
  the ss row gone. `-nP` rendering and
  `lsof -i @127.0.0.1` captured in the s13
  supplement. An unrelated `redis-server`
  listener (port 6399) appears in the ss
  captures — another build's specimen on
  the shared machine, named in the chapter
  rather than trimmed away.
- *Ch. 6:* the OR exhibit (`lsof -p A -i
  :8734` returning A's 15 rows plus B's 2),
  `-a` making the same pair empty (exit 1)
  for A and exact for B, `-c tail`, and the
  `-d` trap: `-p A,B -d cwd` *without* `-a`
  returned every process's cwd plus both
  full tables (kept whole in s07). The
  corrected list and `^` exclusion forms
  were re-captured cleanly in s07b
  (`-a -p A,B -d cwd` → 2 rows;
  `-a -p A,^B -d cwd` → 1 row).
- *Ch. 7:* `-Fpcfn` field output via `tr`,
  and the shipped `examples/open-files.sh`
  run against the planted holder (15 rows,
  planted files last). Exit codes captured:
  `-p 999999` → 1, an existing-but-unopened
  file → 1. The search-mode anomaly
  measured in s11: three consecutive `+D`
  runs over a tree with a held file → exit
  1 each (s04 shows the rows themselves),
  and `+L1` with nothing to find → exit 0
  (also the tail of s05). `-r 2` under
  `timeout 3`: two snapshots, `=======`
  separators, exit 124 attributed to
  `timeout` in the text.
- *Ch. 8:* the scratch user end to end —
  `useradd` (exit 0), root's holder
  invisible to specimen by file (exit 1)
  and skeletal by pid (cwd/rtd/txt
  `unknown`, a `NOFD` line, exit 0),
  specimen's own tail by file and by pid in
  full, `can't stat()` warnings on
  specimen's runs (tmpfs and squashfs
  mounts belonging to the sandbox), and
  `userdel -r` + `id specimen` failing,
  both captured. Root's `lsof -u specimen`
  is also in the transcript — see the
  sandbox note below.
- *Ch. 9:* every recipe is a command from
  an earlier chapter's capture; the one new
  form, the `-d` exclusion list
  (`-d ^mem,^cwd,^rtd,^txt`), was captured
  in s12 against a planted holder (only
  fds 0–4 survived, as intended).
- *Ch. 10:* `fuser -v` on the planted file
  (`f....`) and port (`F....`);
  `/proc/22552/fd` listed beside the same
  tail's lsof table (fd 3 the log, fd 4
  `anon_inode:inotify`); `fuser -k` killed
  the tail and the death was verified by
  lsof (exit 1) and `pgrep -a tail`
  (exit 1). `netstat` is present on the
  build machine (`/usr/bin/netstat`) — its
  mapping to `ss` is stated as the known
  succession, not re-taught.

**Capture hygiene (declared trims):** three
`-p` tables are quoted with a `...` elision
over their `mem` rows in chapters 2 and 6
(the full tables are in the transcripts);
specimen's repeated `can't stat()` warning
pairs are shown once per command (each
warning printed twice per run in the raw
capture, once per lsof pass); a planted
process's start line is annotated with its
pid in brackets where the shell reported it
out of order. No output row quoted in a
chapter was altered. Two exploratory probe
runs (before the numbered sessions) fell
into shell traps of their own — a `cd … &&`
chain backgrounding a different pid than
expected, and a `pkill -f` pattern matching
the probe shell's own command line; both
were diagnosed from their captures, nothing
from them is quoted, and the final cleanup
checks (below) were run after them.

**The build sandbox's confession:** the
lab ran as the sandbox's root, which is
confined: processes started through `su`
live in a neighbouring compartment, and
even root's readlinks into them are denied
— so root's `lsof -u specimen` shows
skeleton rows too (s09). On a stock system
root sees full tables for all users; the
chapter says so and the skeleton *shapes*
are exactly those a non-owner sees, which
is the transferable content. The sandbox's
filesystems also appear as overlay devices
(`0,86`, `0,42`) and its `/home` refuses
some operations other guides in this series
have met; none of that changes lsof's
answers, only some NAME paths.

**Documented-only (not run), and why:**

- *NFS behaviour.* No NFS mount exists on
  the build machine. lsof on an unresponsive
  NFS server can itself block while
  stat-ing files on the mount — named in
  the README and chapter 3 as documented
  behaviour, with no capture claimed.
- *macOS and BSD lsof.* Same lineage,
  different defaults and some different
  flags (macOS lsof lacks some GNU-era
  conveniences and adds its own); named in
  the README and here, not captured — no
  such machine in the lab.
- *Stock-system root visibility.* The
  direction that matters (a non-owner's
  skeleton view) is captured; root's
  unrestricted view on a stock system is
  stated from the kernel's `/proc`
  permission rules, with the sandbox's
  contrary artefact declared above rather
  than hidden.
- *Installation.* The build machine
  already had lsof 4.95.0; other platforms'
  packaging is described, not performed.

**Cleanup, verified after the final
session:** no `hold.py`, `listen.py`, or
planted `tail`/`sleep` processes remain
(pgrep checks); port 8734 has no listener
(`ss`); the scratch user `specimen` does
not exist (`id` fails); the 200 MiB
specimen was deleted and its space
recovered in-session (chapter 4's own
numbers); the lab tree retains only its
small planted text files and the
transcripts.

Specimen discipline, for the record: the
only credentials in the guide are none at
all; the only user created was the scratch
account above, removed on the record; every
planted process was killed by the session
that planted it.
