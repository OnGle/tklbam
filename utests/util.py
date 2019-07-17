import sys
from os.path import dirname, abspath, join
from os import lstat, readlink, remove, mkdir, chmod
import os
import shutil
import tarfile
import stat
import subprocess

sys.path.append(dirname(dirname(abspath(__file__))))
testroot = dirname(abspath(__file__))

def get_path_info(path):
    st = lstat(path)
    return {
        'mode': st.st_mode,
        'uid': st.st_uid,
        'gid': st.st_gid,
        'size': st.st_size,
        'mtime': int(st.st_mtime),
        'symlink': readlink(path) if stat.S_ISLNK(st.st_mode) else None
    }

def setup():
    mkdir('test_tmp')
    tf = tarfile.TarFile(join(testroot, 'test_data/testdir.tar'))
    tf.extractall(join(testroot, '.'))
    tf.close()

def cleanup():
    shutil.rmtree(join(testroot, 'test_tmp'), ignore_errors=True)
    shutil.rmtree(join(testroot, 'testdir'), ignore_errors=True)

def mv(src, dest):
    shutil.move(src, dest)

def ln_s(src, dest):
    os.symlink(src, dest)

def appendToFile(path, text):
    with open(path, 'a') as fob:
        fob.write(text)
def writeToFile(path, text):
    with open(path, 'w') as fob:
        fob.write(text)

def chgrp(path, gid):
    shutil.chown(path, user=None, group=gid)
def chown(path, uid, gid=None):
    shutil.chown(path, user=uid, group=gid)
def touch(path):
    with open(path, 'w') as fob:
        fob.write('')
def rm(path):
    remove(path)
def rmr(path):
    shutil.rmtree(path)
def rmrf(path):
    shutil.rmtree(path, ignore_errors=True)

def assert_stat(assertEquals, path, mode=None, uid=None, gid=None):
    st = os.stat(path)
    if not mode is None: assertEquals(st.st_mode & 0o777, mode)
    if not uid is None: assertEquals(st.st_uid, uid)
    if not gid is None: assertEquals(st.st_gid, gid)

def is_installed(package):
    try:
        subprocess.check_output(['dpkg-query', '-l', package], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False
