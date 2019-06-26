#!/usr/bin/env python3
#
# Copyright (c) 2010-2012 Liraz Siri <liraz@turnkeylinux.org>
#
# This file is part of TKLBAM (TurnKey GNU/Linux BAckup and Migration).
#
# TKLBAM is open source software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
#
"""Change passphrase of backup encryption key

Options:

    --random    Choose a secure random password (and print it)

"""

import sys
import getopt

import hub
import keypacket
from registry import registry, hub_backups
from passphrase import *

def usage(e=None):
    if e:
        print("error: " + str(e), file=sys.stderr)

    print("Usage: %s [-options]" % sys.argv[0], file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ["help", "random"])
    except getopt.GetoptError as e:
        usage(e)

    opt_random = False
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        if opt == '--random':
            opt_random = True

    hb = hub_backups()

    if opt_random:
        passphrase = random_passphrase()
        print(passphrase)
    else:
        print("(For no passphrase, just press Enter)")
        passphrase = get_passphrase()

    key = keypacket.fmt(registry.secret, passphrase)
    hbr = registry.hbr

    # after we setup a backup record
    # only save key to registry if update_key works
    if hbr:
        try:
            hb.update_key(hbr.backup_id, key)
            registry.key = key

            print(("Updated" if passphrase else "Removed") + \
                    " passphrase - uploaded key to Hub.")

        except hub.Error:
            raise
    else:
        registry.key = key

if __name__=="__main__":
    main()
