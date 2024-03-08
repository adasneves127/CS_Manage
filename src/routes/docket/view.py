from app import app
from src.utils.templates import send_template
from src.utils.db_utils import connect
from flask import session, request, redirect
from src.utils import exceptions

@app.route('/docket/officer/view/')
def view_officer_docket():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    if not conn.can_user_view_officer_docket(session['user']):
        return exceptions.InvalidPermissionException()    

    if conn.can_user_view_officer_docket(session['user']):
        return send_template('docket/index.liquid')

@app.route('/docket/officer/table/', methods = ['POST'])
def get_officer_docket_table():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    if not conn.can_user_view_officer_docket(session['user']):
        return exceptions.InvalidPermissionException()    

    docket_records = conn.get_officer_docket()
    return send_template('docket/table.liquid', records = docket_records)
    
@app.route("/docket/officer/view/<int:seq>", methods=["GET"])
def get_officer_docket(seq):
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_view_officer_docket(user):
        return exceptions.InvalidPermissionException()
    
    docket_info = conn.search_officer_docket(seq)
    return send_template("docket/single.liquid", docket = docket_info[0],
                         votes=docket_info[1], assignees=docket_info[2])

@app.route("/docket/officer/assigned/table/", methods=['POST'])
def get_assigned_records_table():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_view_officer_docket(user):
        return exceptions.InvalidPermissionException()
    docket_records = conn.get_assigned_records(user)
    return send_template('docket/table.liquid', records = docket_records) 

@app.route("/docket/officer/assigned/")
def get_assigned_records():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_view_officer_docket(user):
        return exceptions.InvalidPermissionException()
    
    return send_template("docket/assigned.liquid")