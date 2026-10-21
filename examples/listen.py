#!/usr/bin/env python3
"""listen.py -- hold a TCP listener and a UDP socket on one loopback port.

Usage: listen.py [PORT]        (default 8734)

Accepted TCP connections are kept open and never answered, so a client
that connects stays ESTABLISHED for as long as the listener lives.
Prints its PID, then sleeps until killed. Part of the lsof guide's lab;
the shipped copy lives in the guide repo's examples/.
"""

import os
import socket
import sys
import threading
import time


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8734
    tcp = socket.socket()
    tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp.bind(("127.0.0.1", port))
    tcp.listen(5)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("127.0.0.1", port))
    held = []

    def accept_loop():
        while True:
            conn, _addr = tcp.accept()
            held.append(conn)  # keep it open; never answer

    threading.Thread(target=accept_loop, daemon=True).start()
    print(f"listen.py pid {os.getpid()} holding tcp+udp 127.0.0.1:{port}",
          flush=True)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
