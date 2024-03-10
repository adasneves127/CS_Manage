from app import app
from src.utils.db_utils import connect
from flask import session, redirect, request
from src.utils.templates import send_template
from src.utils import exceptions

@app.route('/admin/finance/status/', methods=['GET'])
def get_finance_statuses():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_invoice_admin(user.seq):
        statuses = conn.get_all_finance_statuses()
        return send_template('admin/finance/status.liquid', statuses=statuses, page="Finance")
    else:
        raise exceptions.InvalidPermissionException()

@app.route("/admin/finance/status/", methods=['POST'])
def post_finance_status():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_invoice_admin(user.seq):
        if 'id' in request.json:
            conn.update_finance_status(request.json['id'], request.json['name'], session['user'])
            return "OK", 201
        else:
            conn.create_finance_status(request.json['name'], session['user'])
        return "OK", 201
    else:
        raise exceptions.InvalidPermissionException()
    

@app.route('/admin/docket/status/', methods=['GET'])
def get_docket_statuses():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_invoice_admin(user.seq):
        statuses = conn.get_all_docket_statuses()
        return send_template('admin/finance/status.liquid', statuses=statuses, page="Docket")
    else:
        raise exceptions.InvalidPermissionException()

@app.route("/admin/docket/status/", methods=['POST'])
def post_docket_status():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_invoice_admin(user.seq):
        if 'id' in request.json:
            conn.update_docket_status(request.json['id'], request.json['name'], session['user'])
            return "OK", 201
        else:
            conn.create_docket_status(request.json['name'], session['user'])
        return "OK", 201
    else:
        raise exceptions.InvalidPermissionException()