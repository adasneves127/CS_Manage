from app import app
from flask import session, request, redirect
from src.utils.templates import send_template
from src.utils.db_utils import connect
from src.utils import exceptions


@app.route("/finances/edit/<int:seq>/", methods=["GET"])
def edit_record(seq):
    connection = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    if not connection.can_user_view_finances(session['user'].seq):
        raise exceptions.InvalidPermissionException()
    record = connection.get_record_by_seq(seq)
    return send_template("finances/edit.liquid", record=record,
                            statuses=connection.get_all_statuses(),
                            approvers=connection.get_all_approvers())
    
@app.route("/finances/edit/<int:seq>", methods=["PATCH"])
def patch_record(seq):
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        
        creator_auth = connection.check_invoice_info(request.json['auth']['creator'], request.json['auth']['creatorPin'])
        print(request.json)
        if creator_auth is None:
            return "Err: Creator not found", 401

        if not creator_auth[0] and not creator_auth[1]:
            return "Err: Auth Info not correct", 401
        
        
        approver_auth = connection.check_invoice_info(request.json['auth']['approver'], request.json['auth']['approverPin'])
        if approver_auth is None:
            return "Err: Approver not found", 401
        
        if not approver_auth[0] and not approver_auth[2]:
            return "Err: Auth Info not correct", 401
        
        connection.edit_record(seq, request.form)
        return redirect("/finances/")
    else:
        raise exceptions.InvalidPermissionException()