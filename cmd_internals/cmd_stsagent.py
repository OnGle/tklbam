#!/usr/bin/python
#
# Copyright (c) 2015 Liraz Siri <liraz@turnkeylinux.org>
#
# This file is part of TKLBAM (TurnKey GNU/Linux BAckup and Migration).
#
# TKLBAM is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
#
"""Ask Hub to use IAM role to get temporary credentials to your TKLBAM S3 storage"""

import sys
from registry import hub_backups
import hub
from retry import retry

@retry(5, backoff=2)
def get_credentials(hb):
    return hb.get_credentials()

def usage(e=None):
    if e:
        print("error: " + str(e), file=sys.stderr)

    print("Syntax: %s" % sys.argv[0], file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(1)

def fatal(e):
    print("error: " + str(e), file=sys.stderr)
    sys.exit(1)

def format(creds):
    values = [ creds[k] for k in ('accesskey', 'secretkey', 'sessiontoken', 'expiration') ]
    return " ".join(values)


def main():
    args = sys.argv[1:]
    if args:
        usage()

    try:
        hb = hub_backups()
    except hub.Backups.NotInitialized as e:
        print("error: " + str(e), file=sys.stderr)

    creds = get_credentials(hb)
    if creds.type != 'iamrole':
        fatal("STS agent incompatible with '%s' type credentials" % creds.type)

    print(format(creds))

if __name__ == "__main__":
    main()
