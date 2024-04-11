from app import app
from flask import session, request, redirect
from src.utils import exceptions
from src.utils.db_utils import db_connection
from src.utils.templates import send_template


@app.route("/docket/officer/vote/<int:seq>", methods=["GET"])
def get_vote_page(seq):
    if "user" not in session:
        raise exceptions.UserNotSignedInException()
    user = session["user"]
    with db_connection() as conn:
        docket = conn.search_officer_docket(seq)[0]

        if docket[8] == "No Vote":
            return send_template('docket/vote.liquid', docket=docket,
                                 non_votable=True)

        if not user.vote[docket[8]]:
            raise exceptions.InvalidPermissionException()

        if docket[3] != 'In Vote':
            raise exceptions.DocketNotVoting()

        has_voted = conn.has_user_voted(user, seq)
        return send_template("docket/vote.liquid", docket=docket,
                             has_voted=has_voted, non_votable=False)


@app.route("/docket/officer/vote/<int:seq>", methods=["POST"])
def save_officer_vote(seq):
    if "user" not in session:
        raise exceptions.UserNotSignedInException()
    user = session["user"]
    with db_connection() as conn:
        docket = conn.search_officer_docket(seq)[0]
        if not user.vote[docket[8]]:
            raise exceptions.InvalidPermissionException()

        vote = request.form["vote_type"]
        conn.save_vote(user, vote, seq)
        return redirect("/docket/officer/view/")


@app.route("/docket/officer/vote/calculate/", methods=["POST"])
def close_vote():
    if "user" not in session:
        raise exceptions.UserNotSignedInException()
    user = session["user"]
    with db_connection() as conn:
        if not user.docket_vote:
            raise exceptions.InvalidPermissionException()

        seq = request.json["docket"]
        conn.close_vote(seq, user)
        return "OK", 200
