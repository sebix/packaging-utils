#!/bin/bash

for pkg in "$@"; do
    SAVEIFS=$IFS   # Save current IFS
    IFS=$'\n'      # Change IFS to new line
    pkgdir=( $(fd --exclude 'home*' -t d $* ${PACKAGING_DIR:-$HOME/packaging}/) )
    IFS=$SAVEIFS   # Restore IFS

    if [ ${#pkgdir[@]} -eq 0 ]; then
        echo "No package directory for $pkg found!"
    elif [ ${#pkgdir[@]} -gt 1 ]; then
        echo "Found ${#pkgdir[@]} dirs: ${pkgdir[@]}"
    else
        echo "Switching to $pkgdir";
        pushd $pkgdir
        echo "Running osc up"
        osc update
        echo "Running updater"
        set -e
        specfile-version-updater
        osc build --ccache --no-verify || osc build --ccache --no-verify --clean
        changelog=$(changelog-extractor)
        osc vc -m "$changelog"
        osc commit -m "$changelog"
        popd
    fi
done
