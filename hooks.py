import os
from os.path import *

from registry import registry
import subprocess
from subprocess import check_output, CalledProcessError

from conf import Conf

class HookError(Exception):
    pass

def _is_signed(fpath, keyring):
    fpath_sig = fpath + ".sig"
    if not exists(fpath_sig):
        return False

    try:
        check_output("gpg --keyring=%s --verify" % keyring, fpath_sig)
        return True
    except CalledProcessError::
        return False

def _run_hooks(path, args, keyring=None):
    if not isdir(path):
        return

    for fname in os.listdir(path):
        fpath = join(path, fname)
        if not os.access(fpath, os.X_OK):
            continue

        if fpath.endswith(".sig"):
            continue

        if keyring and not _is_signed(fpath, keyring):
            continue

        try:
            subprocess.run(fpath, *args)
        except CalledProcessError as e:
            raise HookError("`%s %s` non-zero exitcode (%d)" % \
                            (fpath, " ".join(args), e.returncode))

class Hooks:
    """
    Backup hook invocation:

        pre hook
        create extras
        inspect hook
        run duplicity to create/update backup archives
        post hook

    Restore hook invocation:

        pre hook
        run duplicity to get extras + overlay
        inspect hook
        apply restore to system
        post hook

    """
    BASENAME = "hooks.d"
    LOCAL_HOOKS = os.environ.get("TKLBAM_HOOKS", join(Conf.DEFAULT_PATH, BASENAME))

    PROFILE_KEYRING = "/etc/apt/trusted.gpg.d/turnkey.gpg"

    def __init__(self, name):
        self.name = name

    def _run(self, state):

        _run_hooks(self.LOCAL_HOOKS, (self.name, state))
        if registry.profile:
            _run_hooks(join(registry.profile, self.BASENAME), (self.name, state), keyring=self.PROFILE_KEYRING)

    def pre(self):
        self._run("pre")

    def post(self):
        self._run("post")

    def inspect(self, extras_path):
        orig_cwd = os.getcwd()

        os.chdir(extras_path)
        self._run("inspect")
        os.chdir(orig_cwd)

backup = Hooks("backup")
restore = Hooks("restore")
