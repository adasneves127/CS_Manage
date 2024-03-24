#! /bin/bash

if [ "$EUID" -eq 0 ]
  then echo "Do not run as root. This script will ask for sudo permissions when needed."
  exit
fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo 'Adding Python PPA Repository'
sudo add-apt-repository ppa:deadsnakes/ppa -y >> /dev/null
echo 'Updating Apt Repositories'
sudo apt-get update >> /dev/null
echo 'Installing Python and MySQL Server'
sudo apt-get install python3.12-full python3.12-venv python3.12 mysql-server-8.0 -y >> /dev/null

if [[ ! -d $SCRIPT_DIR/.venv ]];
then
  echo 'Creating Venv'
  python3.12 -m venv $SCRIPT_DIR/.venv >> /dev/null
  $SCRIPT_DIR/.venv/bin/pip install -r $SCRIPT_DIR/requirements.txt > /dev/null
fi

if [[ -z "`sudo mysql -qfsBe "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='management'" 2>&1`" ]];
then 
	echo 'Initializing Database'
	sudo mysql -u root < db_setup.sql
else
	echo 'Database already found'
fi

if [[ ! -d /etc/systemd/system/Management.service ]];
then
  echo "[Unit]
  Description=Gunicorn instance to serve Management Portal
  After=network.target

  [Service]
  User=www-data
  Group=www-data
  WorkingDirectory=$SCRIPT_DIR
  Environment=\"PATH=$SCRIPT_DIR/.venv/bin\"
  ExecStart=$SCRIPT_DIR/.venv/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 app:app
  Restart=on-failure
  RestartSec=5s

  [Install]
  WantedBy=multi-user.target" | sudo tee /etc/systemd/system/Management.service > /dev/null

  sudo usermod -aG $USER www-data
  sudo systemctl daemon-reload
  sudo systemctl start Management.service
  sudo systemctl enable Management.service

  echo "Management Service has been setup"
  echo "Please configure Nginx or Apache to serve the Management Portal"
  echo "File path to serve: $SCRIPT_DIR/myproject.sock"
  echo -e "Example NGINX Setup: \n"
  echo "server {
      server_name <your_domain>;

      location / {
          include proxy_params;
          proxy_pass http://unix:$SCRIPT_DIR/myproject.sock;
      }
  }
  "
fi

#write out current crontab
sudo crontab -l > mycron || :
sudo chown $USER mycron
#echo new cron into cron file
echo "0 0 * * * $SCRIPT_DIR/cron.sh" >> mycron
#install new cron file
sudo crontab mycron
rm mycron
