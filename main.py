#!/usr/bin/env python3
"""main.py - copy entry.png to MAKEFUN_OUTPUT_DIR and verify its sha256.

Stdlib only, no network. Deterministic: the output is a byte-identical copy
of the pre-built entry.png, so both runs produce identical hashes.
"""

import hashlib
import os
import shutil

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    if not os.path.exists(SRC):
        raise FileNotFoundError("missing image: {}".format(SRC))
    os.makedirs(OUT, exist_ok=True)
    dest = os.path.join(OUT, "entry.png")
    shutil.copyfile(SRC, dest)
    h_src = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    h_dst = hashlib.sha256(open(dest, "rb").read()).hexdigest()
    if h_src != h_dst:
        raise AssertionError("sha256 mismatch after copy")
    print(h_src)


if __name__ == "__main__":
    main()