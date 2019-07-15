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
import sys
import os
import re
import subprocess

from fnmatch import fnmatch

class Error(Exception):
    pass

def installed():
    """Return list of installed packages"""

    def parse_status(path):
        control = b""
        with open(path, 'rb') as fob:
            for line in fob:
                if not line.strip():
                    yield control
                    control = b""
                else:
                    control += line

        if control.strip():
            yield control

    packages = []
    for control in parse_status("/var/lib/dpkg/status"):
        d = dict([ re.split(b':\s*', line, 1)
                   for line in control.split(b'\n')
                   if line and (b':' in line) and (line[0] != b' ') ])

        if b"ok installed" in d[b'Status']:
            packages.append(d[b'Package'])

    return packages

class Packages(set):
    @classmethod
    def fromfile(cls, path):
        with open(path, 'rb') as fob:
            packages = fob.read().strip().split(b'\n')
        return cls(packages)

    def tofile(self, path):
        packages = list(self)
        packages.sort()

        with open(path, 'w') as fob:
            for package in packages:
                fob.write(package+'\n')

    def __init__(self, packages=None):
        """If <packages> is None we get list of packages from the package
        manager.
        """
        if packages is None:
            packages = installed()

        set.__init__(self, packages)

class AptCache(set):
    Error = Error

    def __init__(self, packages):
        command = [b"apt-cache", b"show", *packages]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            output, _ = proc.communicate()
            status = proc.returncode
        except subprocess.CalledProcessError as e:
            output = ''
            status = e.returncode
        
        status = os.WEXITSTATUS(status)
        if status not in (0, 100):
            raise self.Error("execution failed (%d): %s\n%s" % (status, command, output))

        cached = [ line.split()[1]
                   for line in output.split(b"\n") if
                   line.startswith(b"Package: ") ]

        super().__init__(cached)

class Blacklist:
    def __init__(self, patterns):
        self.patterns = patterns

    def __contains__(self, val):
        if self.patterns:
            for pattern in self.patterns:
                if fnmatch(val, pattern):
                    return True
        return False

def installable(packages, blacklist=[]):
    installed = Packages()
    aptcache = AptCache(packages)
    blacklist = Blacklist(blacklist)

    installable = []
    skipped = []
    for package in set(packages):
        if package in installed:
            continue

        if package not in aptcache:
            skipped.append(package)
            continue

        if package in blacklist:
            skipped.append(package)
            continue

        installable.append(package)

    return installable, skipped

class Installer:
    """
    Interface::
        installer.command       Command executed
        installer.installable   List of packages to be installed
        installer.skipping      List of packages we're skipping
                                (e.g., because we couldn't find them in the apt-cache)

        installer()             Run installation command and return an error code
                                By default noninteractive...
    """
    Error = Error

    def __init__(self, packages, blacklist=None):
        self.installable, self.skipping = installable(packages, blacklist)
        self.installed = None

        self.installable.sort()
        self.skipping.sort()

        if self.installable:
            self.command = [b"apt-get", b"install", b"--assume-yes", *self.installable]
        else:
            self.command = None

    def __call__(self, interactive=False):
        """Install packages. Return (exitcode, output) from execution of installation command
        """
        if not self.installable:
            raise Error("no installable packages")

        command = self.command
        if not interactive:
            command = ["DEBIAN_FRONTEND=noninteractive", *command]

        sys.stdout.flush()
        sys.stderr.flush()

        packages_before = Packages()
        retval = subprocess.run(command).returncode
        packages_after = Packages()

        self.installed = packages_after - packages_before
        return retval
