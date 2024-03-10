from app import app
from src.utils.templates import send_template
from flask import session, redirect, request
from src.utils.db_utils import connect
from src.utils import exceptions

@app.route('/admin/record/', methods=['GET'])
def get_record_types():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_invoice_admin(user.seq):
        return send_template('admin/record_types.liquid', types=conn.get_all_record_types())

@app.route('/admin/record/', methods=['POST'])
def post_record_type():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_invoice_admin(user.seq):
        if 'id' in request.json:
            conn.update_record_type(request.json['id'], request.json['name'], session['user'])
            return "OK", 201
        else:
            conn.create_record_type(request.json['name'], session['user'])
        return "OK", 201
    else:
        raise exceptions.InvalidPermissionException()