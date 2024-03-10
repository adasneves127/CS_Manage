#! /bin/bash



SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

sudo systemctl stop Management.service
# The user will get a 502 should they try to access the page during this period
$SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/db_backup.py
sudo systemctl restart mysql.service
sudo systemctl start Management.service