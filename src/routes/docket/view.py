from app import app
from src.utils.templates import send_template
from src.utils.db_utils import connect
from flask import session, request, send_file, make_response
from src.utils import exceptions
import tempfile
import base64
import os

@app.route('/docket/officer/view/')
def view_officer_docket():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    if not conn.can_user_view_officer_docket(session['user']):
        raise exceptions.InvalidPermissionException()    

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
    print(docket_records)
    
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
    print(docket_info)
    docket_records = docket_info[0]
    docket_record_data = list(docket_records[0:2]) + \
        [docket_records[2].split("\n")] + \
        list(docket_records[3:])
    docket_viewers = conn.get_docket_viewers()
    return send_template("docket/single.liquid", docket = docket_record_data,
                         votes=docket_info[1], assignees=docket_info[2],
                         attachments=docket_info[3],
                         users=docket_viewers)

@app.route("/docket/officer/assigned/table/", methods=['POST'])
def get_assigned_records_table():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_view_officer_docket(user):
        return exceptions.InvalidPermissionException()
    docket_records = conn.get_assigned_records(user)
    print(docket_records)
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

@app.route("/docket/attach/view/<int:seq>", methods=['GET'])
def view_docket_attachment(seq: int):
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    if not conn.can_user_view_officer_docket(user):
        return exceptions.InvalidPermissionException()
    
    file_data = conn.search_docket_attachments(seq)
    
    # with tempfile.TemporaryDirectory() as temp_dir:
    with open(file_data[0], 'wb') as f:
        file_contents = base64.b64decode(file_data[1])
        f.write(file_contents)
        
    resp = make_response(send_file(file_data[0]))
    resp.mimetype = "application/octet-stream"

    os.remove(file_data[0])
    #print(f"os.remove({file_data[0]})")
    return resp
    