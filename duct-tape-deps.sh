#!/bin/bash -eu

BASE_DIR="$PWD"
DEPROOT="$BASE_DIR/lib/deps"
TMP="$BASE_DIR/debian/tmp/tklbam-deps"
HOST_ARCH=$(dpkg --print-architecture)

export LD_LIBRARY_PATH="$DEPROOT/bin"

mkdir -p "$DEPROOT" "$TMP"

pypy_arch=
case $HOST_ARCH in
    amd64)
        pypy_arch="linux64";;
    arm64)
        pypy_arch="aarch64";;
    *)
        echo "ERROR: $HOST_ARCH unsupported" >&2
        exit 1;;
esac

read -r pypy_checksum pypy_archive <<< "$( \
    sed -n "/pypy2\.7.*$pypy_arch/{s|<*.*>||;p;q;}" "checksums.txt" \
)"

cd "$TMP" || exit 1

wget "https://downloads.python.org/pypy/$pypy_archive"

if [[ $(sha256sum "$pypy_archive") != "$pypy_checksum"*"$pypy_archive" ]]; then
    echo "ERROR: $pypy_archive checksum mismatch" >&2
    exit 1
fi

echo "unpacking $pypy_archive..."
tar -xf "$pypy_archive" --transform "s|^${pypy_archive%.tar.bz2}/||" -C "$DEPROOT"

while IFS= read -r line; do
    pkg="${line%:*}"
    commit_id="${line##*:}"

    git clone "https://github.com/turnkeylinux/$pkg"
    cd "$pkg" || exit 1
    git checkout "$commit_id"
    "$LD_LIBRARY_PATH/pypy" setup.py build
    cd "$TMP" || exit 1
    mv "$pkg/build/lib"*/* "$DEPROOT/site-packages"
done < "$BASE_DIR/dep-commit-ids"
