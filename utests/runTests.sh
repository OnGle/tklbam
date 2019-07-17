#!/bin/bash

usage() {
    echo "./runTests.sh [-v|--verbose]"
    exit 1
}

if [[ -n "$1" ]]; then
    if [[ "$1" == "-v" || "$1" == "--verbose" ]]; then
        VERBOSE='-v'
    else
        usage
    fi
else
    VERBOSE=''
fi

GREEN="$(printf '\u001b[32m')"
RED="$(printf '\u001b[31m')"
YELLOW="$(printf '\u001b[33m')"

BOLD="$(printf '\u001b[1m')"
RESET="$(printf '\u001b[0m')"

TESTDIR="$(dirname "$(realpath $0)")"

python3 -m unittest discover $VERBOSE -s $TESTDIR 2>&1 |\
    sed -e "s/Test\(.*\)FAIL\(.*\)$/${RED}${BOLD}Test\1FAIL\2${RESET}/g" |\
    sed -e "s/Test\(.*\)skipped\(.*\)$/${YELLOW}${BOLD}Test\1skipped\2${RESET}/g" |\
    sed -e "s/Test\(.*\)ok\(.*\)$/${GREEN}${BOLD}Test\1ok\2${RESET}/g"
