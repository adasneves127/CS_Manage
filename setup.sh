#! /bin/bash

if [ "$EUID" -eq 0 ]
  then echo "Do not run as root. This script will ask for sudo permissions when needed."
  exit
fi


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


echo "[Unit]
Description=Gunicorn instance to serve Management Portal
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$SCRIPT_DIR
Environment=\"PATH=$SCRIPT_DIR/.venv/bin\"
ExecStart=$SCRIPT_DIR/.venv/bin/gunicorn --reload --workers 3 --bind unix:myproject.sock -m 007 app:app

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/Management.service > /dev/null

sudo usermod -aG $USER www-data

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

#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "0 2 * * 1 $SCRIPT_DIR/cron.sh" >> mycron
#install new cron file
crontab mycron
rm mycron
