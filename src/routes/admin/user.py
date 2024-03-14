from app import app
from src.utils.db_utils import connect
from flask import session, redirect, request
from src.utils.templates import send_template
from src.utils import exceptions

@app.route("/admin/users/", methods=['GET'])
def get_admin_users_index():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_user_admin(user.seq):
        return send_template('admin/users.liquid', users=conn.get_all_users())
    else:
        raise exceptions.InvalidPermissionException()

@app.route("/admin/users/edit", methods=['GET'])
def edit_user():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_user_admin(user.seq):
        return send_template('admin/user.liquid', user=conn.get_user_by_seq(request.args['seq']).__dict__)
    else:
        raise exceptions.InvalidPermissionException()

@app.route("/admin/users/edit", methods=['POST'])
def update_user():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_user_admin(user.seq):
        seq = request.args['seq']
        data = request.form
        vals = (
            data.get('username'),
            data.get('email'),
            data.get('first_name'),
            data.get('last_name'),
            data.get('theme'),
            data.get('system_user') == 'on',
            data.get('enable_emails') == 'on',
            data.get('inv_view') == 'on',
            data.get('inv_edit') == 'on',
            data.get('inv_admin') == 'on',
            data.get('approve_invoices') == 'on',
            data.get('doc_view') == 'on',
            data.get('doc_edit') == 'on',
            data.get('doc_admin') == 'on',
            data.get('user_admin') == 'on',
            data.get('doc_vote') == 'on'
        )
        
        conn.update_user(seq, vals, user)
        return """<script>window.close();</script>"""
    else:
        raise exceptions.InvalidPermissionException()

@app.route("/admin/users/add/", methods=['GET'])
def add_user():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_user_admin(user.seq):
        return send_template('admin/new_user.liquid')
    else:
        raise exceptions.InvalidPermissionException()

@app.route("/admin/users/add/", methods=['POST'])
def add_user_post():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    user = session['user']
    if conn.is_user_admin(user.seq):
        data = request.form
        vals = (
            data.get('username'),
            data.get('email'),
            data.get('first_name'),
            data.get('last_name'),
            data.get('theme'),
            data.get('system_user') == 'on',
            data.get('enable_emails') == 'on',
            data.get('inv_view') == 'on',
            data.get('inv_edit') == 'on',
            data.get('inv_admin') == 'on',
            data.get('approve_invoices') == 'on',
            data.get('doc_view') == 'on',
            data.get('doc_edit') == 'on',
            data.get('doc_admin') == 'on',
            data.get('user_admin') == 'on',
            data.get('doc_vote') == 'on'
        )
        conn.add_user(vals, user)
        return redirect("/admin/users/"), 201
    else:
        raise exceptions.InvalidPermissionException()