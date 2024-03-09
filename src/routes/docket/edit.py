from app import app
from src.utils.templates import send_template
from src.utils.db_utils import connect
from flask import session, request, redirect
from src.utils import exceptions


@app.route("/docket/officer/edit/<int:seq>", methods=["GET"])
def edit_officer_docket(seq):
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_edit_officer_docket(user):
        return exceptions.InvalidPermissionException()
    
    # Check if the user has permission for that individual docket
    if not conn.can_user_edit_docket_record(user, seq):
        return exceptions.InvalidPermissionException()
    
    docket, votes, assignees = conn.search_officer_docket(seq)
    return send_template("docket/edit.liquid", docket=docket,
                         votes=votes, assignees=assignees,
                         statuses = conn.get_all_docket_statuses())


@app.route("/docket/officer/edit/<int:seq>", methods=["POST"])
def update_officer_docket(seq):
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_edit_officer_docket(user):
        return exceptions.InvalidPermissionException()
    
    # Check if the user has permission for that individual docket
    if not conn.can_user_edit_docket_record(user, seq):
        return exceptions.InvalidPermissionException()
    
    docket = request.form
    conn.update_officer_docket(docket, user, seq)

@app.route("/docket/officer/assignee/add/", methods=["POST"])
def add_assignee():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_edit_officer_docket(user):
        return exceptions.InvalidPermissionException()
    
    data = request.json
    seq = data['docket']
    if not conn.can_user_edit_docket_record(user, seq):
        return exceptions.InvalidPermissionException()
    user_data = conn.get_user_by_full_name(data['name'])
    conn.add_assignee((seq, user_data, user.seq))
    return redirect(f"/docket/officer/edit/{seq}")

@app.route("/docket/officer/assignee/del/", methods=["POST"])
def del_assignee():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_edit_officer_docket(user):
        return exceptions.InvalidPermissionException()
    
    data = request.json
    seq = data['docket']
    if not conn.can_user_edit_docket_record(user, seq):
        return exceptions.InvalidPermissionException()
    conn.del_assignee((seq, data['user'], user.seq))
    return redirect(f"/docket/officer/edit/{seq}")