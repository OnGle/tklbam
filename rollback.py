#
# Copyright (c) 2010-2013 Liraz Siri <liraz@turnkeylinux.org>
#
# This file is part of TKLBAM (TurnKey GNU/Linux BAckup and Migration).
#
# TKLBAM is open source software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
#
import os
import sys
from os.path import *

import stat
import shutil

from datetime import datetime
from paths import Paths as _Paths

import mysql
import pgsql

from changes import Changes
from dirindex import DirIndex
from pkgman import Packages

import utils
import traceback

class Error(Exception):
    pass

class Rollback:
    Error = Error

    PATH = "/var/backups/tklbam-rollback"
    class Paths(_Paths):
        files = [ 'etc', 'etc/mysql',
                  'fsdelta', 'dirindex', 'originals',
                  'newpkgs', 'myfs', 'pgfs' ]

    @classmethod
    def create(cls, path=PATH):
        if exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        os.chmod(path, 0o700)

        self = cls(path)

        os.mkdir(self.paths.etc)
        os.mkdir(self.paths.originals)
        return self

    def __init__(self, path=PATH):
        """deletes path if it exists and creates it if it doesn't"""

        if not exists(path):
            raise Error("No such directory " + repr(path))

        self.paths = self.Paths(path)
        self.timestamp = datetime.fromtimestamp(os.stat(path).st_ctime)

    @staticmethod
    def _move(source, dest):
        if not lexists(source):
            raise Error("no such file or directory " + repr(source))

        if not exists(dirname(dest)):
            os.makedirs(dirname(dest))

        utils.remove_any(dest)
        utils.move(source, dest)

    def _move_to_originals(self, source):
        """Move source into originals"""
        dest = join(self.paths.originals, source.strip('/'))
        self._move(source, dest)

    def _move_from_originals(self, dest):
        """Move path from originals to dest"""
        source = join(self.paths.originals, dest.strip('/'))
        self._move(source, dest)

    def rollback_files(self):
        if not exists(self.paths.fsdelta):
            return

        changes = Changes.fromfile(self.paths.fsdelta)
        dirindex = DirIndex(self.paths.dirindex)

        exceptions = 0
        for change in changes:
            try:
                if change.path not in dirindex:
                    utils.remove_any(change.path)
                    continue

                if change.OP in ('o', 'd'):
                    try:
                        self._move_from_originals(change.path)
                    except self.Error:
                        continue

                dirindex_rec = dirindex[change.path]
                local_rec = DirIndex.Record.frompath(change.path)

                if dirindex_rec.uid != local_rec.uid or \
                   dirindex_rec.gid != local_rec.gid:
                    os.lchown(change.path, dirindex_rec.uid, dirindex_rec.gid)

                if dirindex_rec.mod != local_rec.mod:
                    mod = stat.S_IMODE(dirindex_rec.mod)
                    os.chmod(change.path, mod)
            except:
                exceptions += 1
                # fault-tolerance: warn and continue, don't die
                traceback.print_exc(file=sys.stderr)

        for fname in ('passwd', 'group'):
            shutil.copy(join(self.paths.etc, fname), "/etc")

        if exceptions:
            raise Error("caught %d exceptions during rollback_files" % exceptions)

    def rollback_new_packages(self):
        if not exists(self.paths.newpkgs):
            return

        rollback_packages = Packages.fromfile(self.paths.newpkgs)
        current_packages = Packages()

        purge_packages = current_packages & rollback_packages
        if purge_packages:
            os.system("DEBIAN_FRONTEND=noninteractive dpkg --purge " + " ".join(purge_packages))

    def rollback_database(self):
        if exists(self.paths.myfs):
            mysql.restore(self.paths.myfs, self.paths.etc.mysql,
                          add_drop_database=True)

        if exists(self.paths.pgfs):
            pgsql.restore(self.paths.pgfs)

    def rollback(self):
        exceptions = 0
        for method in (self.rollback_database, self.rollback_files, self.rollback_new_packages):
            try:
                method()
            except:
                exceptions += 1
                print("error: %s raised an exception:" % method.__name__, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

        shutil.rmtree(self.paths)
        if exceptions:
            raise Error("caught %d exceptions during rollback" % exceptions)

    def save_files(self, changes, overlay_path):
        for fname in ("passwd", "group"):
            shutil.copy(join("/etc", fname), self.paths.etc)

        changes.tofile(self.paths.fsdelta)
        di = DirIndex()
        for change in changes:
            if lexists(change.path):
                di.add_path(change.path)
                if change.OP in ('o', 'd'):
                    if change.OP == 'o' and not lexists(overlay_path + change.path):
                        continue
                    self._move_to_originals(change.path)
        di.save(self.paths.dirindex)

    def save_new_packages(self, packages):
        packages = list(packages)
        packages.sort()

        with open(self.paths.newpkgs, 'w') as fob:
            for package in packages:
                fob.write(package+'\n')

    def save_database(self):
        try:
            mysql.backup(self.paths.myfs, self.paths.etc.mysql)
        except mysql.Error:
            pass

        try:
            pgsql.backup(self.paths.pgfs)
        except pgsql.Error:
            pass

