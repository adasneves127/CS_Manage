from app import app
from src.utils.templates import send_template
from src.utils.db_utils import db_connection
from flask import session, request, redirect
from src.utils import exceptions
from src.utils.file_utils import is_file_valid_type, valid_file_types


@app.route("/docket/officer/edit/<int:seq>", methods=["GET"])
def edit_officer_docket(seq):
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_edit_officer_docket(user):
            raise exceptions.InvalidPermissionException()

        # Check if the user has permission for that individual docket
        if not conn.can_user_edit_docket_record(user, seq):
            raise exceptions.InvalidPermissionException()

        docket, votes, assignees, attach = conn.search_officer_docket(seq)
        statuses = conn.get_all_docket_statuses()

        return send_template(
            "docket/edit.liquid",
            docket=docket,
            votes=votes,
            assignees=assignees,
            statuses=statuses,
            attachments=attach,
            users=conn.get_docket_viewers(),
        )


@app.route("/docket/officer/edit/<int:seq>", methods=["POST"])
def update_officer_docket(seq):
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_edit_officer_docket(user):
            return exceptions.InvalidPermissionException()

        # Check if the user has permission for that individual docket
        if not conn.can_user_edit_docket_record(user, seq):
            return exceptions.InvalidPermissionException()

        docket = request.form
        conn.update_officer_docket(docket, user, seq)
        return redirect("/docket/officer/view/")


@app.route("/docket/officer/assignee/add/", methods=["POST"])
def add_assignee():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_edit_officer_docket(user):
            return exceptions.InvalidPermissionException()

        data = request.json
        seq = data["docket"]
        if not conn.can_user_edit_docket_record(user, seq):
            return exceptions.InvalidPermissionException()
        conn.add_assignee((seq, data["user"], user.seq))
        return redirect(f"/docket/officer/edit/{int(seq)}")


@app.route("/docket/officer/assignee/del/", methods=["POST"])
def del_assignee():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_edit_officer_docket(user):
            return exceptions.InvalidPermissionException()

        data = request.json
        seq = data["docket"]
        if not conn.can_user_edit_docket_record(user, seq):
            return exceptions.InvalidPermissionException()
        conn.del_assignee((seq, data["user"], user.seq))
        return redirect(f"/docket/officer/edit/{seq}")


@app.route("/docket/officer/attach/<int:seq>", methods=["POST"])
def add_attachment(seq: int):
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_edit_officer_docket(user):
            return exceptions.InvalidPermissionException()

        docket_seq = request.json["docket"]
        file_name = request.json["file_name"]
        file_data = request.json["file_data"]
        if not is_file_valid_type(file_name, file_data):
            return (
                f"""File must be one of the following formats:
    {', '.join([x[1] for x in valid_file_types])}""",
                400,
            )
        # Get the existing attachments for this docket
        attachments = conn.get_docket_attachments(docket_seq)
        for item in attachments:
            if item[1] == file_name:
                conn.update_attachment(item[0], file_data)
                return "OK", 200

        conn.add_attachment(docket_seq, file_name, file_data, user)
        return "OK", 200
