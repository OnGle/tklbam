#!/bin/bash -eu

# Run this script to update the version of pypy to be dynamically downloaded
# when building the tklbam deb package. Will always download the latest pypy.

# pypy arch -> debian arch:
# - linux64 = amd64
# - aarch64 = arm64

SUPPORTED_ARCH=(linux64 aarch64)

tmp_file=$(mktemp)

curl --silent https://pypy.org/checksums.html --output "$tmp_file"

echo "# pypy versions and checksums - run ./update_pypy.sh to update" > \
    checksums.txt
for arch in "${SUPPORTED_ARCH[@]}"; do
    sed -n "/pypy2\.7.*$arch/{s|<*.*>||;p;q;}" "$tmp_file" >> checksums.txt
done
rm -rf "$tmp_file"
if git diff --quiet HEAD -- checksums.txt; then
    echo "no update available - checksums.txt unchanged"
else
    echo "checksums.txt updated; double check and commit"
    # non-zero exit if there's something to do
    exit 1
fi
