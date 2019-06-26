#!/usr/bin/python
# 
# Copyright (c) 2013 Liraz Siri <liraz@turnkeylinux.org>
# 
# This file is part of TKLBAM (TurnKey GNU/Linux BAckup and Migration).
# 
# TKLBAM is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
# 
"""
Dump PostgreSQL databases to a filesystem path.
"""
from os.path import *

import sys
import pgsql

def fatal(e):
    print("fatal: " + str(e), file=sys.stderr)
    sys.exit(1)

def usage(e=None):
    if e:
        print("error: " + str(e), file=sys.stderr)

    print("Syntax: %s path/to/output [ -?database/table ... ] " % sys.argv[0], file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(1)

def main():
    args = sys.argv[1:]
    if not args:
        usage()

    outdir = args[0]
    limits = args[1:]

    pgsql.backup(outdir, limits)

if __name__ == "__main__":
    main()

