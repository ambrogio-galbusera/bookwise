#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/admin/bookwise
python -m http.server 9000
cd /
