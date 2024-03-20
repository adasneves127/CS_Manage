# Club Management System | Programmed March 2024

## Created by Alex Dasneves and Lyra Brown

---

# Setup

## App Requirements

This system is designed to run on an Ubuntu Server, running NGINX. To configure this system, your account ***must*** have root/sudo access.

### Application Configuration

To begin configuring this application, run the `setup.sh` script. This script will:

* Install Python 3.12
* Install MySQL Server 8.0
* Configure your Python Virtual Environment
* Initialize the MySQL Server
* Create a Systemd Service to serve this project using Gunicorn
* Provide instructions on how to configure NGINX to serve this server
* Create a Crontask (Service that runs at specified intervals) to backup the database and restart the server every week.

After running the `setup.sh` script, run the command `source .venv/bin/activate` to use the configured version of Python.

Next run `python config_app.py`. This app will configure a file containing the application information, as well as a basic system administrator account.