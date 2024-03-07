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