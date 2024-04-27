#!/bin/bash -x
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

echo "User $(whoami)"
which python
cd /
cd home/admin/bookwise
python bookwise.py
cd /
