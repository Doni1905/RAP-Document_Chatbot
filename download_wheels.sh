#!/bin/bash
set -e

# Directory to store wheels
mkdir -p wheels

# Download all wheels for requirements.txt
pip download --platform manylinux2014_x86_64 --python-version 310 --only-binary=:all: --dest wheels -r requirements.txt

echo "All wheels downloaded to ./wheels/" 