from src.utils.db_utils import connect
from src.utils.containers import User
import json
import secrets
from getpass import getpass

def create_user(conn: connect):
    
    user_data = User.create_user()
    conn.save_user(user_data)
    # Get a password and an approval pin
    password = getpass("Enter a password for the new user: ")
    pin = getpass("Enter an approval pin for the new user: ")
    conn.change_password(user_data.seq, user_data, password)
    conn.change_approver_pin(user_data.seq, user_data, pin)

def config_app_info():
    system_name = input("Enter the name of this system: ")
    deployed_location = input("Enter the location of this system's deployment: ")
    about_text = []
    
    while (line_text := input("Enter the text for this system's 'about' page [End with blank line]: ")) != "":
        about_text.append(line_text)
    
    email_domain = input("Enter the email domain for this system: ")
    app_domain = input("Enter the URL for this system [Include http:// or https://]: ")
    app_info_full = {
        "public":{
            "system_name": system_name,
            "deployed_location": deployed_location,
            "about_text": about_text,
            "email_domain": email_domain,
            "application_url": app_domain,
            "system_administrator": {
                "name": "",
                "email": "",
            },
            "application_administrators": [
                {
                    "name": "",
                    "email": "",
                }
            ],
            "enable_smtp": False,
        },
        "private": {
            "secret_token": secrets.token_hex(),
            "smtp": {
                "server": "smtp server",
                "port": "smtp port",
                "user": "smtp user",
                "password": "smtp password",
                "from": "email box name",
                "from_email": "email box email",
                "use_tls": "true/false",
                "use_ssl": "true/false",
                "cc": [],
                "bcc": []
            },
            "doc_thresh": 2/3
        }
    }
    app_info = app_info_full["public"]
    print("Please review the following information:")
    print(f"System Name: {app_info['system_name']}")
    print(f"Deployed Location: {app_info['deployed_location']}")
    print(f"About Text: ")
    for line in app_info['about_text']:
        print(line)
    print(f"Email Domain: {app_info['email_domain']}")
    if input("Is this information correct? (y/n): ").lower() == 'y':
        with open("app_info.json", "w") as f:
            json.dump(app_info_full, f, indent=4)
        print("Please review app_info.json and populate the " +  
            "system_administrator and application_administrators" + 
            " fields with the appropriate information.")
        print("If you would like to enable emailing, please" + 
              " modify the 'smtp' related fields, " + 
              "and set 'enable_smtp' to 'true'")
        print("Please Note: Password Reset requires SMTP to be enabled")
        print("App Info Saved")
    else:
        print("App Info Not Saved")
    
    

if __name__ == "__main__":
    print("Configuring Application Information")
    config_app_info()
    config_dot_env()
    x = connect()
    print("Creating Administrative User")
    create_user(x)
    