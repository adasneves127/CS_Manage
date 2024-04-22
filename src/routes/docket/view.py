from app import app
from src.utils.templates import send_template
from src.utils.db_utils import db_connection
from flask import session, send_file, make_response, request
from src.utils import exceptions
import base64
import tempfile


@app.route("/docket/officer/view/")
def view_officer_docket():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()

        if not conn.can_user_view_officer_docket(session["user"]):
            raise exceptions.InvalidPermissionException()

        if conn.can_user_view_officer_docket(session["user"]):
            return send_template("docket/index.liquid")


@app.route("/docket/officer/table/", methods=["GET"])
def get_officer_docket_table():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()

        if not conn.can_user_view_officer_docket(session["user"]):
            return exceptions.InvalidPermissionException()

        docket_records = conn.get_officer_docket()

        return send_template("docket/table.liquid", records=docket_records)


@app.route("/docket/officer/view/<int:seq>", methods=["GET"])
def get_officer_docket(seq):
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_view_officer_docket(user):
            return exceptions.InvalidPermissionException()

        docket_info = conn.search_officer_docket(seq)
        (docket_info)
        docket_records = docket_info[0]
        docket_record_data = (
            *docket_records[:2], docket_records[2].split("\n"),
            *docket_records[3:])
        docket_viewers = conn.get_docket_viewers()
        return send_template(
            "docket/single.liquid",
            docket=docket_record_data,
            votes=docket_info[1],
            assignees=docket_info[2],
            attachments=docket_info[3],
            users=docket_viewers,
            conversations=conn.get_docket_conversations(seq)
        )


@app.route("/docket/officer/assigned/table/", methods=["POST"])
def get_assigned_records_table():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_view_officer_docket(user):
            return exceptions.InvalidPermissionException()
        docket_records = conn.get_assigned_records(user)
        (docket_records)
        return send_template("docket/table.liquid", records=docket_records)


@app.route("/docket/officer/assigned/")
def get_assigned_records():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_view_officer_docket(user):
            return exceptions.InvalidPermissionException()

        return send_template("docket/assigned.liquid")


@app.route("/docket/attach/view/<int:seq>", methods=["GET"])
def view_docket_attachment(seq: int):
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_view_officer_docket(user):
            return exceptions.InvalidPermissionException()

        file_data = conn.search_docket_attachments(seq)

        with tempfile.NamedTemporaryFile(delete_on_close=False, delete=False) as tempFile:
            file_contents = base64.b64decode(file_data[1])
            tempFile.write(file_contents)
            tempFile.flush()

           
            return send_file(tempFile.name, as_attachment=True,
                            download_name=file_data[0])
