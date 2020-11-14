#!/usr/bin/env bash

echo Updating and cloning the submodules...

git submodule update --init > /dev/null 2>&1
git submodule foreach git checkout main > /dev/null 2>&1
