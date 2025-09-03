#!/bin/bash

pypy_root='pypy2.7-v7.3.20-linux64'
pypy_archive="$pypy_root.tar.bz2"

DEPROOT="$(pwd)/debian/tmp/dh-*/deproot"

mkdir -p $DEPROOT /usr/lib/tklbam/deps

cd debian/tmp

wget "https://downloads.python.org/pypy/$pypy_archive"
tar -xvf "$pypy_archive"

pypy_root="$(pwd)/$pypy_root"

rm "$pypy_archive"

git clone https://github.com/turnkeylinux/python-crypto
cd python-crypto
LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$pypy_root/bin" "$pypy_root/bin/python2" setup.py build

cd ..
git clone https://github.com/turnkeylinux/python-pycurl
cd python-pycurl
LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$pypy_root/bin" "$pypy_root/bin/python2" setup.py build

cd ..
mv pypy*/* $DEPROOT
mv python-crypto/build/lib*/* $DEPROOT/site-packages
rm -rf python-crypto
mv python-pycurl/build/lib*/* $DEPROOT/site-packages
rm -rf python-pycurl
cd ..
