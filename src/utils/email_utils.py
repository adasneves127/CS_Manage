from src.utils import containers
from src.utils.app_utils import load_app_info
from email.utils import formataddr
import smtplib
from email.message import EmailMessage
import base64
import bs4

def get_logo_img():
    try:
        open('interface/static/logo.png', 'rb').close()
    except FileNotFoundError:
        return ""
    
    logo_img = open('interface/static/logo.png', 'rb')
    logo = base64.b64encode(logo_img.read()).decode('utf-8')
    return f"""<img id="logo" src="data:image/png;base64, {logo}">"""

def getStyleData():
    return """
<style>
            @media only screen and (min-width: 768px) {
                #logo{
                    width: 20em;
                }
            }
            #logo{
                width: 5em;
            }
            
            
        </style>"""

def send_password_updated_email(user_obj: containers.User):
    email = user_obj.email
    if user_obj.system_user:
        return
    
    if not user_obj.receive_emails:
        return
    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    email += email_domain
    subject = '[Alert] Password Updated'


    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                Your password has been updated. If you did not make this change, please contact your application administrators as soon as possible.
            </p>
            <p>
            Administrators: <br/>
        
    """
    for admin in app_info['public']['application_administrators']:
        body_html += f'{admin['name']}, <a href="mailto:{admin['email']}{email_domain}">Email</a><br/>'

    body_html += f"""
    </p>
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, [], [])


def send_pin_reset_email(user_obj: containers.User):
    email = user_obj.email
    if user_obj.system_user:
        return

    if not user_obj.receive_emails:
        return

    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    email += email_domain
    subject = '[Alert] Finance Pin Updated'


    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                Your finance pin has been updated.
                If you did not make this change, please contact your
                 application administrators as soon as possible.
            </p>

    """
    for admin in app_info['public']['application_administrators']:
        body_html += f'''<p>Administrator: {admin['name']},
        <a href="mailto:{admin['email']}{email_domain}">Email</a></p>'''

    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, [], [])


def send_password_reset_email(user_obj: containers.User, reset_link: str):
    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    email = user_obj.email
    email += email_domain
    subject = '[Alert] Password Reset Requested'

    if user_obj.system_user:
        return

    if not user_obj.receive_emails:
        return

    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                A request to reset your password has been made. <br/>
                Please use this link to reset your password:
                <a href="{reset_link}"> Reset Password</a>
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, [], [])

def send_assignment_email(target_user: containers.User,
                          from_user: containers.User,
                          docket_data: tuple):
    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    email = target_user.email
    email += email_domain
    subject = '[Notice] Docket Record Assigned'

    if target_user.system_user:
        return

    if not target_user.receive_emails:
        return

    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                You have been added as an assignee to an officer docket item. <br/>
                <br>
                Docket Information: {docket_data[0][0]}<br/>
                Docket Title: {docket_data[0][1]}<br/>
                Docket Description: {docket_data[0][2]}<br/>
                Docket Status: {docket_data[0][3]}<br/>
                <br>
                You have been added to this record by {from_user.full_name}. <br/>
                You can view this record by logging into the application and navigating to the assigned docket record page. <br/>
                We encourage you to reach out to {from_user.full_name}, and any other assignees for more information. <br/>
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, [from_user.email + email_domain], [])

def alert_docket_removal(target_user: containers.User, from_user: containers.User, docket_data: tuple):
    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    email = target_user.email
    email += email_domain
    subject = '[Notice] Docket Record Assignment Removed'

    if target_user.system_user:
        return

    if not target_user.receive_emails:
        return

    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                You have been removed as an assignee to an officer docket item. <br/>
                <br>
                Docket Information: {docket_data[0][0]}<br/>
                Docket Title: {docket_data[0][1]}<br/>
                Docket Status: {docket_data[0][3]}<br/>
                <br>
                You have been removed from this record by {from_user.full_name}. <br/>
                We encourage you to reach out to {from_user.full_name} for more information. <br/>
                
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, [from_user.email + email_domain], [])

def alert_docket_creation(creation_user, docket_all_users, docket_data, docket_seq):
    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    email = creation_user.email
    email += email_domain
    subject = '[Notice] Docket Record Created'
    cc_list = []
    for user in docket_all_users:
        cc_list.append(user[4] + email_domain)

    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                A new docket item has been created. <br/>
                <br>
                Docket ID: {docket_seq}<br/>
                Docket Title: {docket_data['title']}<br/>
                Docket Status: Proposed <br/>
                <br>
                This item was created by {creation_user.full_name}. If you have any questions, please reach out to them. <br/>
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
            <br/>
            [This email was sent to you as a voting member of the officer board. If you believe this was sent in error, please contact your application administrators.]
        </body>
    </html>
    """
    send_email(subject, body_html, email, cc_list, [])

def alert_docket_update(creation_user, assignee_users, docket_data):
    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    email = creation_user.email
    email += email_domain
    subject = '[Notice] Docket Record Updated'
    cc_list = []
    for user in assignee_users:
        cc_list.append(user['email'] + email_domain)
    

    body_html = f"""
    <html>
        <head>
        {getStyleData()}
            
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                A docket item has updated. <br/>
                <br>
                Docket ID: {docket_data[0][0]}<br/>
                Docket Title: {docket_data[0][1]}<br/>
                Docket Status: {docket_data[0][3]} <br/>
                <br>
                This item was updated by {creation_user.full_name}. If you have any questions, please reach out to them. <br/>
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
            <br/>
            <p>[This email was sent to you for one of the following reasons: </p>
            <ul>
                <li>You created this docket</li>
                <li>You are assigned to this docket item</li>
            </ul>
            <p>If you believe this was sent in error, please contact your application administrators.]</p>
        </body>
    </html>
    """
    send_email(subject, body_html, email, cc_list, [])

def send_bug_report(bug_form: dict, userInfo: containers.User):
    app_info = load_app_info()
    email_domain = app_info['public']['email_domain']
    subject = '[CRITICAL] Bug Report Submitted'
    cc_list = [
        x['email'] + email_domain
        for x in app_info['public']['application_administrators']
    ]
    to_user = app_info['public']['system_administrator']['email'] + email_domain

    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                
                You are receiving this email because a bug report has been submitted, and you are listed as an administrator account in the system. <br/>
                Bug Report Information: <br/>
                <br/>
                Datetime Occured: {bug_form['dt_occured']}<br/>
                Bug Description: {bug_form['description']}<br/>
                Reporter Information:
                <table>
                    <tr>
                        <th>User Full Name</th>
                        <td>{userInfo.full_name}</td>
                    </tr>
                    <tr>
                        <th>User Seq</th>
                        <td>{userInfo.seq}</td>
                    </tr>
                    <tr>
                        <th>User Name</th>
                        <td>{userInfo.user_name}</td>
                    </tr>
                    <tr>
                        <th>User Email</th>
                        <td><a href="mailto:{userInfo.email}{email_domain}">Email</a></td>
                    </tr>
                </table>
                For more user information, please visit the user management and administration page <br/>
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
            <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, to_user, cc_list, [])
    
def notify_vote_confirmation(user: containers.User, vote, doc_info):
    app_info = load_app_info()
    email = user.email + app_info['public']['email_domain']
    subject = '[Notice] Vote Confirmed'

    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                
                You are receiving this email because your vote has been confirmed. <br/>
                Vote Type: {vote}<br/>
                Docket ID: {doc_info[0][0]}<br/>
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
            <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, [], [])
    
def send_backup_file():
    app_info = load_app_info()
    email = app_info['public']['system_administrator']['email'] + app_info['public']['email_domain']
    subject = '[Notice] Weekly Backup Data'
    cc_list = [
        x['email'] + app_info['public']['email_domain']
        for x in app_info['public']['application_administrators']
    ]


    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello, <br>
                
                Please find attached the weekly database backup. <br/>
                Please keep this file safe, and do not distribute to unauthorized users. <br/>
            </p>

    """
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
            <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, cc_list, [], [('./backup.sql', "text", "plain")])

def send_welcome_email(user: containers.User, reset_link, finance_pin):
    app_info = load_app_info()
    email = user.email + app_info['public']['email_domain']
    subject = 'Welcome to ' + app_info['public']['system_name']
    app_domain = app_info['public']['application_url']


    body_html = f"""
    <html>
        <head>
        {getStyleData()}
        </head>
        <body>
            {get_logo_img()}
            <p>
                Hello! <br>
                
                Welcome to the {app_info['public']['system_name']} application. <br/>
                
                To finish setting up your account, please use the following link to set your password: <br/>
                <a href="http://{app_domain}/reset_password/{reset_link}">Set Password</a> <br/>
                
                
            </p>

    """
    
    if user.inv_edit or user.approve_invoices or user.inv_admin:
        body_html += f"Your financial record pin is {finance_pin}<br/> <br/>"
    
    body_html += f"""
            Kind Regards, <br>
            The Application Development & Support Team <br/>
            {app_info['public']['system_name']} <br/>
            {app_info['public']['deployed_location']} <br/>
            <br/>
        </body>
    </html>
    """
    send_email(subject, body_html, email, [], [])


def send_email(subject, body, email, cc: list, bcc: list, attachement_paths: list = []):
    app_info = load_app_info()

    if not app_info['public']['enable_smtp']:
        return False

    email_domain = app_info['public']['email_domain']

    msg = EmailMessage()
    smtp_settings = app_info['private']['smtp']
    msg['Subject'] = subject
    msg['From'] = formataddr((smtp_settings['from'],
                              (smtp_settings['from_email'] + email_domain)))
    msg['To'] = email
    msg['Cc'] = ', '.join(cc)
    msg['Bcc'] = ', '.join(bcc)
    msg.add_header('reply-to', smtp_settings['from_email'] + email_domain)
    msg.set_content(body, 'html')
    msg.add_alternative(bs4.BeautifulSoup(body, "html.parser").text, 'plain')
    for attachement in attachement_paths:
        with open(attachement[0], 'rb') as file:
            file_data = file.read()
            file_name = file.name
            msg.add_attachment(file_data, maintype=attachement[1], subtype=attachement[2], filename=file_name)

    # Send the message via  the defined SMTP server.
    smtp_host = smtp_settings['server'] + ":" + str(smtp_settings['port'])
    if smtp_settings['use_ssl']:
        s = smtplib.SMTP_SSL(smtp_host)
    else:
        s = smtplib.SMTP(smtp_host)

    if smtp_settings['use_tls']:
        s.starttls()

    s.login(smtp_settings['user'], smtp_settings['password'])

    to_addrs = [email]
    cc_addrs = cc
    bcc_addrs = bcc
    from_addr = smtp_settings['from_email'] + email_domain
    to_list = to_addrs + cc_addrs + bcc_addrs
    s.sendmail(from_addr, to_list, msg.as_string())
    s.quit()
