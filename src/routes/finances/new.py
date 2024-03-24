from app import app
from src.utils.templates import send_template
from src.utils.db_utils import connect
from flask import request, session, abort
from mysql.connector.errors import DatabaseError
from src.utils import exceptions
import requests
from src.utils.app_utils import load_app_info
from base64 import b64encode

@app.route("/finances/new/", methods=["GET"])
def new_record():
    connection = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    if connection.can_user_view_finances(session['user'].seq):
        return send_template("finances/new.liquid", types=connection.get_all_types(),
                             statuses=connection.get_all_finance_status_names(),
                             users=connection.get_all_finance_users(),
                             approvers=connection.get_all_approvers())
    else:
        raise exceptions.InvalidPermissionException()
    
@app.route("/finances/new/", methods=["POST"])
def create_record():
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        # Check the post auth info
        # let auth_info = {
        #        "creator": document.getElementById("Creator").value,
        #        "creatorPin": document.getElementById("creatorPin").value,
        #        "approver": document.getElementById("Approver").value,
        #        "approverPin": document.getElementById("approverPin").value
        #    }
        creator_auth = connection.check_invoice_info(request.json['auth']['creator'], request.json['auth']['creatorPin'])
        if creator_auth is None:
            return "Err: Creator not found", 401

        if not creator_auth[0] and not creator_auth[1]:
            return "Err: Auth Info not correct", 401
        
        approver_auth = connection.check_invoice_info(request.json['auth']['approver'], request.json['auth']['approverPin'])
        if approver_auth is None:
            return "Err: Approver not found", 401
        
        if not approver_auth[0] and not approver_auth[2]:
            return "Err: Auth Info not correct", 401
        
        try:
            connection.create_record(request.json['record'], session['user'])
            if request.json['record']['header']['approver'] == 'Not Approved':
                seq = connection.create_officer_docket({
                    "title": f"Review Finance ID {request.json['record']['header']['id']}",
                    "body": f"""A new finance request was created by {session['user'].full_name}.
                    Please review and debate this item. Please see attached for item."""
                }, session['user'])
                app_info = load_app_info()
                url = app_info['public']['application_url']
                connection.add_attachment(seq, f'Finance {request.json['record']['header']['id']}.html',
                                          b64encode(
                                              requests.get(f"{url}/finances/view/{seq}",
                                                           json={
                                                               "auth": app_info['private']['secret_token']
                                                           }
                                                       ).content),
                                          session['user']
                                          )
            return "Record created", 200
        except DatabaseError as e :
            if str(e) == "1644 (45000): Cannot approve own invoice":
                return "Err: Unable to approve own finances!", 401
            else:
                raise e
    else:
        raise exceptions.InvalidPermissionException()
    
@app.route("/finances/new/preview/", methods=["POST"])
def preview_record():
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        return send_template("finances/finance_view.liquid", record=request.json, isPreview=True)
    else:
        raise exceptions.InvalidPermissionException()