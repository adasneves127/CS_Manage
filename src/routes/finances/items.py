from app import app
from flask import request, session
from src.utils.templates import send_template
from src.utils.db_utils import connect

@app.route('/finances/item/', methods=['GET'])
def get_items():
    conn = connect()
    if conn.is_invoice_admin(session['user'].seq):
        items = conn.fetch_items()
        return send_template('finances/items.liquid', items=items)

