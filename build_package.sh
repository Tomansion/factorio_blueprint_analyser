#!/bin/bash

# exit when any command fails
set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# Build the package

if test -d "build_package"; then
    echo -e $CYAN"Delete current build saved"$NC
    rm -r build_package
fi

echo -e $CYAN"Build the package"$NC
python setup.py sdist bdist_wheel

echo -e $CYAN"Save tar file"$NC
mkdir build_package
mv dist/*.tar.gz build_package

echo -e $CYAN"Cleaning file"$NC
rm -r dist *.egg-info build

echo -e $GREEN"Build is in build_package folder !"$NC