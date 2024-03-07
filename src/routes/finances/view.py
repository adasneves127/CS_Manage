from app import app
from flask import request, session, redirect
from src.utils.templates import send_template
from src.utils.db_utils import connect
from src.utils import exceptions

@app.route("/finances/table/", methods=["POST", "GET"])
def get_table():
    if request.method == "GET":
        return redirect("/finances/")
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        finance_records = connection.filter_finances(request.json)
        finance_records.sort(key=lambda x: int(x['header']['id']))
        return send_template("finances/table.liquid", records=finance_records), 200
    else:
        raise exceptions.InvalidPermissionException()

@app.route("/finances/view/<int:seq>/", methods=["GET"])
def get_record(seq):
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        record = connection.get_record_by_seq(seq)
        approvers = connection.get_all_approvers()
        return send_template("finances/finance_view.liquid", record=record, isPreview=False)
    else:
        raise exceptions.InvalidPermissionException()
    
@app.route("/finances/table/pending/", methods=["POST", "GET"])
def pending_table():
    if request.method == "GET":
        return redirect("/finances/pending/")
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        print(connection.get_pending_finances())
        return send_template("finances/table.liquid", records=connection.get_pending_finances())
    else:
        raise exceptions.InvalidPermissionException()