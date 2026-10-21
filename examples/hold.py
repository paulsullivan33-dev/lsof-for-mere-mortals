#!/usr/bin/env python3
"""hold.py -- open files and keep them open, so lsof has something to find.

Usage: hold.py FILE[:MODE] [FILE[:MODE] ...]

MODE is one of:
    r   read (the default)
    w   write (creates or truncates)
    u   read+write (the file must already exist)
    d   a directory, opened with os.open

Prints its PID, then sleeps until killed. Part of the lsof guide's lab;
the shipped copy lives in the guide repo's examples/.
"""

import os
import sys
import time


def open_one(spec):
    path, _, mode = spec.partition(":")
    mode = mode or "r"
    if mode == "d":
        return os.open(path, os.O_RDONLY)
    return open(path, {"r": "rb", "w": "wb", "u": "r+b"}[mode])


def main():
    keep = [open_one(spec) for spec in sys.argv[1:]]
    print(f"hold.py pid {os.getpid()} holding {len(keep)} file(s)", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
