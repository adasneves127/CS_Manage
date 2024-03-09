from app import app
from flask import request, session, redirect
from src.utils.templates import send_template
from src.utils.db_utils import connect
from src.utils import exceptions

@app.route('/finances/item/', methods=['GET'])
def get_items():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    
    if conn.is_invoice_admin(session['user'].seq):
        items = conn.fetch_items()
        return send_template('finances/items.liquid', items=items)

@app.route("/finances/item/", methods=["POST"])
def add_item():
    conn = connect()
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    user = session['user']
    
    if conn.is_invoice_admin(user.seq):
        # Gots to do some logic to see if the item is valid, and if we
        # hava another item id that is the same.
        item = request.form
        print(item)
        if item['ID'] == '':
            conn.create_item(item, user)
        else:
            conn.ammend_item(item, user)
    
    return redirect('/finances/item/')
        

