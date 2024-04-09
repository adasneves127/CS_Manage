from app import load_app_info


def password_reset_email(User) -> str:
    app_info = load_app_info()
    email_str = ""

    email_str += """<html>"
    <head>
"
    <style>"
    body {"
        font-family: Arial, sans-serif;"
    }"
    </style>"
    </head>"""
    email_str += "<body>"

    # Email should be:
    """
    Dear {User.first_name} {User.last_name},
    Welcome to {app_info['system_name']}. We have received a request to reset
    your password. If you did not request this, please contact your system
    administrator. <br>
    To reset your password, please click the following link: <br>
    <a href="{app_info['application_url']}/reset_password/{User.user_name}">
    Reset Password</a> <br>
    If the link does not work, please copy and paste the following URL into
    your browser: <br>
    {app_info['application_url']}/reset_password/{User.user_name} <br>
    Thank you, <br>
    {app_info['system_name']} Administrators
    <br><br><br>
    This is a system-generated email.
    """

    email_str += f"""Dear {User.first_name} {User.last_name},<br>
    Welcome to {app_info['system_name']}. We have received a request to reset
    your password. If you did not request this, please contact your system
    administrator. <br>
    To reset your password, please click the following link: <br>
    <a href="{app_info['application_url']}/reset_password/{User.user_name}">
    Reset Password</a> <br>
    If the link does not work, please copy and paste the following URL into
    your browser: <br>
    {app_info['application_url']}/reset_password/{User.user_name} <br>
    Thank you, <br>
    {app_info['system_name']} Administrator
    <br><br><br>
    This is a system-generated email. To unsubscribe, please contact your
    system administrator.
    """

    email_str += "</body>"
    email_str += "</html>"

    return email_str
