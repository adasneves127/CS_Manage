from app import app
from flask import request, session, redirect
from src.utils.templates import send_template
from src.utils.db_utils import connect
from src.utils import exceptions
from src.utils.app_utils import load_app_info


@app.route("/finances/table/", methods=["POST", "GET"])
def get_table():
    if request.method == "GET":
        return redirect("/finances/")
    connection = connect()
    if connection.can_user_view_finances(session["user"].seq):
        finance_statuses = connection.get_all_finance_status_names()
        finance_types = connection.get_all_types()
        print(request.json)
        request_data = {
            "status": {
                status: request.json.get(status)
                for status in finance_statuses
                if request.json.get(status) is True
            },
            "types": {
                req_type: request.json.get(req_type)
                for req_type in finance_types
                if request.json.get(req_type) is True
            },
        }
        finance_records = connection.filter_finances(request_data)
        return_data = send_template("finances/table.liquid",
                                    records=finance_records), 200
        # Input is sterilized before hitting database. Database does not
        # contain any script tags or other data. Liquid handles rendering
        # HTML special characters by encoding them to their &abbr; tags.
        # deepcode ignore XSS: Records are fetched directly from DB. See above.
        return return_data
    else:
        raise exceptions.InvalidPermissionException()


@app.route("/finances/view/<int:seq>/", methods=["GET"])
def get_record(seq):
    connection = connect()
    secret = load_app_info()["private"]["secret_token"]
    given_secret = ""
    if request.is_json:
        given_secret = secret
    if given_secret == secret or (
        session.get("user") is not None and connection
            .can_user_view_finances(session.get("user").seq)
    ):

        record = connection.get_record_by_seq(seq)
        return send_template(
            "finances/finance_view.liquid", record=record, isPreview=False
        )
    else:
        raise exceptions.InvalidPermissionException()


@app.route("/finances/table/pending/", methods=["POST", "GET"])
def pending_table():
    if request.method == "GET":
        return redirect("/finances/pending/")
    connection = connect()
    if connection.can_user_view_finances(session["user"].seq):
        return send_template(
            "finances/table.liquid", records=connection.get_pending_finances()
        )
    else:
        raise exceptions.InvalidPermissionException()
