#!/bin/bash -eu


tmp_file="$(mktemp -d)"

COMMIT_ID_PATH="$(pwd)/dep-commit-ids"

rm -f "$COMMIT_ID_PATH"

cd "$tmp_file"
for pkg in python-crypto python-pycurl tklbam-duplicity turnkey-pylib tklbam-python-boto pycurl-wrapper; do
    echo "# getting HEAD commit id for $pkg"
    if [[ $pkg == "pycurl-wrapper" ]]; then
        commit_id="$(git ls-remote "https://github.com/turnkeylinux/$pkg" | grep refs/heads/python2 | awk '{ print $1 }')"
    else
        commit_id="$(git ls-remote "https://github.com/turnkeylinux/$pkg" | grep HEAD | awk '{ print $1 }')"
    fi
    echo "$pkg:$commit_id" >> "$COMMIT_ID_PATH"
done

rm -r "$tmp_file"
