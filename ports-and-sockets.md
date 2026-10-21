# Ports and Sockets

**Scope:** lsof against the network — the
`-i` selection, a planted TCP listener and
UDP socket, the rows for a live connection
from both ends at once, and the same
questions put to `ss` until the two tools
agree, including after the listener dies.

## The plant: one process, two sockets

`examples/listen.py` holds a TCP listener
and a UDP socket on the same loopback port,
8734:

```
$ python3 bin/listen.py 8734 &   [started pid 22428]
listen.py pid 22428 holding tcp+udp 127.0.0.1:8734
```

Ask lsof about the port — `-i :8734` selects
Internet sockets by port — and both handles
come back:

```
$ lsof -i :8734
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22428 root    3u  IPv4 857701      0t0  TCP localhost:8734 (LISTEN)
python3 22428 root    4u  IPv4 857702      0t0  UDP localhost:8734 
[exit 0]
```

Sockets wear their file-table clothes:
descriptor numbers (3 and 4), the both-ways
access letter `u`, TYPE `IPv4`, and a NAME
that is an address instead of a path —
`protocol host:port`, with TCP's state in
parentheses. Two refinements of the
selection, both everyday forms:

```
$ lsof -iTCP:8734 -sTCP:LISTEN
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22428 root    3u  IPv4 857701      0t0  TCP localhost:8734 (LISTEN)
[exit 0]
$ lsof -iUDP:8734
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22428 root    4u  IPv4 857702      0t0  UDP localhost:8734 
[exit 0]
```

`-iTCP` narrows the protocol; `-sTCP:LISTEN`
narrows by state — together they are the
"who is listening on this port" one-liner.
UDP, notice, has no state to show: UDP is
connectionless, so its row just sits there
with no `(LISTEN)` and no peer. A UDP row's
existence *is* the information.

Small honesty note: lsof resolved the
address to the name `localhost` and would
resolve well-known ports to service names
too. For scripts and for unambiguous
reading, `-n` (no name resolution) and `-P`
(ports as numbers) exist; the commands file
keeps the `-nP` habit. Both forms are
captured in the lab (session s13): under
`-nP` the same rows render as
`TCP 127.0.0.1:8734 (LISTEN)`, and
`lsof -i @127.0.0.1` — select by the other
end's address — returned exactly the
planted listener and connection rows.

## A connection, from both ends

The listener accepts connections and holds
them without answering, so a client that
connects stays connected. Plant one:

```
$ curl -s http://127.0.0.1:8734/ &   [started pid 22437; server never answers, so it hangs on]
$ lsof -i :8734
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3 22428 root    3u  IPv4 857701      0t0  TCP localhost:8734 (LISTEN)
python3 22428 root    4u  IPv4 857702      0t0  UDP localhost:8734 
python3 22428 root    5u  IPv4 857074      0t0  TCP localhost:8734->localhost:59048 (ESTABLISHED)
curl    22437 root    5u  IPv4 857074      0t0  TCP localhost:59048->localhost:8734 (ESTABLISHED)
[exit 0]
```

The connection appears **twice**, once per
endpoint, and the NAMEs are mirror images:
the server's accepted socket (a *new*
descriptor, fd 5 — the listener on fd 3 is
still listening) reads
`8734->59048 (ESTABLISHED)`, and the
client's reads `59048->8734 (ESTABLISHED)`.
The client's port, 59048, was chosen by its
kernel from the ephemeral range. When a real
incident asks "which process is talking to
that database," this pair of rows is the
whole answer, and grepping lsof's output for
the far address is a legitimate way to work.

## The cross-check: ss

`ss` is the network-native neighbour (the
*Watching Your System* neighbourhood, met
properly in chapter 10). Put the same
questions to it:

```
$ ss -ltnp
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess                                 
LISTEN 0      0          127.0.0.1:6399      0.0.0.0:*    users:(("redis-server",pid=21798,fd=6))
LISTEN 0      0          127.0.0.1:8734      0.0.0.0:*    users:(("python3",pid=22428,fd=3))     
LISTEN 0      0              [::1]:6399            *:*    users:(("redis-server",pid=21798,fd=7))
[exit 0]
$ ss -lunp
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
UNCONN 0      0          127.0.0.1:8734      0.0.0.0:*    users:(("python3",pid=22428,fd=4))
[exit 0]
```

Same listener, same pid, same fd — 22428's
fd 3 in both tables (and an unrelated
`redis-server` on 6399 that happened to be
running on the build machine; real listings
always have neighbours). During the
connection, `ss -tnp` shows the ESTAB rows
with one detail lsof doesn't offer:
`Recv-Q 77` on the server's side — 77 bytes
sitting unread in its receive queue, which
is the client's HTTP request, unanswered by
design.

The honest comparison, with the lab's
numbers: on this small machine both tools
are effectively instant (`ss -tln` 0.002 s,
`lsof -i` 0.009 s, same session). The
structural difference matters more than the
stopwatch: `ss` asks the kernel's socket
tables directly, while lsof assembles its
answer from every process's descriptor
table — so `ss` stays the sharper tool for
*pure socket* questions (states, queues,
timers), and lsof is the one that also
answers everything *else* a process holds,
including the sockets' owners in the same
breath as their files. And one lsof-only
sight: chapter 4's deleted-but-open file is
invisible to `ss` by construction — it isn't
a socket.

## Proving it ended

Kill the client, kill the listener, ask
both tools again:

```
[listener stopped]
$ lsof -i :8734
[exit 1]
$ ss -ltnp
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess                                 
LISTEN 0      0          127.0.0.1:6399      0.0.0.0:*    users:(("redis-server",pid=21798,fd=6))
LISTEN 0      0              [::1]:6399            *:*    users:(("redis-server",pid=21798,fd=7))
[exit 0]
```

lsof prints nothing and exits 1 — no process
holds port 8734 in any state — and ss's
listener list is back to the unrelated
redis. "The port is free" is a claim the
guide just checked two ways, which is the
standard every chapter is held to.
