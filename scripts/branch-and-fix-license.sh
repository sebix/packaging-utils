#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "2 arguments expected: project and package" >&2
fi
username=$(osc who | egrep -o "^[^:]+")

osc bco "$1" "$2"
pushd "home:$username:branches:$1/$2"
/usr/bin/license-rewriter *.spec
if [[ $? -eq 0 ]]; then
    osc vc -m "Use %license macro for license."
    osc build
    if [[ $? -eq 0 ]]; then
        osc commit -m "Use %license macro for license."
        osc submitpac -m "%license fix. Automatic submission."
    else
        echo "Build failed, aborting." >&2
    fi
else
    echo "License rewrite failed" >&2
fi
popd
