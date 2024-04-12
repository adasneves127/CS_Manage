#! /bin/bash



SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

find $SCRIPT_DIR/backups ! -type d -mtime +2 -delete
sudo systemctl stop Management.service
# The user will get a 502 should they try to access the page during this period
$SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/db_backup.py
mkdir -p $SCRIPT_DIR/backups

sudo mysqldump management > $SCRIPT_DIR/backups/$(date +%s).sql
# Restart the mysql server
sudo systemctl restart mysql.service
# Start the Management service
sudo systemctl start Management.service

# Reboot the Server
sudo reboot now