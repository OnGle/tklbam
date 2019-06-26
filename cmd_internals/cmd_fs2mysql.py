#!/usr/bin/python
# 
# Copyright (c) 2010-2012 Liraz Siri <liraz@turnkeylinux.org>
# 
# This file is part of TKLBAM (TurnKey GNU/Linux BAckup and Migration).
# 
# TKLBAM is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
# 
"""
Map a filesystem created by mysql2fs back to MySQL

Options:
    --tofile=PATH           Write mysqldump output to file (- for STDOUT)
    -v --verbose            Turn on verbosity

    --skip-extended-insert  Skip extended insert (useful in debugging)
    --add-drop-database     Drop databases and then recreate them

Supports the following subset of mysql(1) options:

    -u --user=USER 
    -p --password=PASS

       --defaults-file=PATH
       --host=HOST

"""
import sys
import getopt

import mysql

def usage(e=None):
    if e:
        print("error: " + str(e), file=sys.stderr)

    print("Syntax: %s [-options] path/to/myfs [ -?database/table ... ] " % sys.argv[0], file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'u:p:v', 
                                       ['verbose', 'tofile=',
                                        'skip-extended-insert',
                                        'add-drop-database',
                                        'user=', 'password=', 'defaults-file=', 'host='])
    except getopt.GetoptError as e:
        usage(e)

    opt_verbose = False
    opt_tofile = None
    opt_skip_extended_insert = False
    opt_add_drop_database = False
    myconf = {}
    for opt, val in opts:
        if opt in ('-v', '--verbose'):
            opt_verbose = True
        elif opt == '--tofile':
            opt_tofile = val
        elif opt == '--skip-extended-insert':
            opt_skip_extended_insert = True
        elif opt == '--add-drop-database':
            opt_add_drop_database = True
        elif opt in ('-u', '--user'):
            myconf['user'] = val
        elif opt in ('-p', '--password'):
            myconf['password'] = val
        elif opt == "--defaults-file":
            myconf['defaults_file'] = val
        elif opt == "--host":
            myconf['host'] = val
        else:
            usage()

    if not args:
        usage()

    myfs = args[0]
    limits = args[1:]

    if opt_tofile:
        if opt_tofile == '-':
            fh = sys.stdout
        else:
            fh = file(opt_tofile, "w")
    else:
        fh = mysql.mysql(**myconf)

    callback = None
    if opt_verbose:
        print("destination: " + fh.name)
        callback = mysql.cb_print()

    if opt_verbose:
        pass

    mysql.fs2mysql(fh, myfs, limits, callback, 
                   opt_skip_extended_insert,
                   opt_add_drop_database)

if __name__ == "__main__":
    main()
