from app import app
from flask import request, session, redirect
from src.utils.templates import send_template
from src.utils.db_utils import db_connection
from src.utils import exceptions
from src.utils.app_utils import load_app_info


@app.route("/finances/table/", methods=["POST"])
def get_table():
    with db_connection() as connection:
        if connection.can_user_view_finances(session["user"].seq):
            data = {
                "status": {},
                "types": {}
            }

            print(request.json)
            if request.is_json:
                data = request.json
            finance_records = connection.filter_finances(data)
            return_data = send_template("finances/table.liquid", False,
                                        records=finance_records), 200
            # Input is sterilized before hitting database. Database does not
            # contain any script tags or other data. Liquid handles rendering
            # HTML special characters by encoding them to their &abbr; tags.
            # deepcode ignore XSS: Records are fetched directly from DB.
            return return_data
        else:
            raise exceptions.InvalidPermissionException()


@app.route("/finances/view/<int:seq>/", methods=["GET"])
def get_record(seq):
    with db_connection() as connection:
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
    with db_connection() as connection:
        if connection.can_user_view_finances(session["user"].seq):
            return send_template(
                "finances/table.liquid",
                records=connection.get_pending_finances()
            )
        else:
            raise exceptions.InvalidPermissionException()
