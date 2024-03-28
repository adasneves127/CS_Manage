SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "server {
      server_name localhost;

      location / {
          include proxy_params;
          proxy_pass http://unix:$SCRIPT_DIR/myproject.sock;
      }
}" | sudo tee /etc/nginx/sites-available/management
sudo ln -s /etc/nginx/sites-available/management /etc/nginx/sites-enabled/management
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx