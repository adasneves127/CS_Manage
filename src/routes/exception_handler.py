from app import app
from src.utils import exceptions
from flask import session, request
from src.utils.templates import send_template


@app.errorhandler(404)
def page_not_found_404(e):
    return send_template("exceptions/404.liquid"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return send_template("exceptions/500.liquid"), 500


@app.errorhandler(exceptions.InvalidPermissionException)
def invalid_permission(e: exceptions.InvalidPermissionException):
    return send_template("exceptions/invalidPermissions.liquid"), 403


@app.errorhandler(exceptions.UserNotSignedInException)
def return_user_sign_in_with_ref_url(e: exceptions.UserNotSignedInException):
    session["ref"] = request.path
    heading = "This page requires authorization to view. "
    heading += "Please sign in to continue.",
    return send_template(
        "login.liquid",
        heading=heading
    ), 401


@app.errorhandler(exceptions.UserNotFoundException)
def return_user_sign_in_not_found(e: exceptions.UserNotFoundException):
    heading = "Your username or password is incorrect, "
    heading += "or your account is not active."""
    return send_template(
        "login.liquid",
        heading=heading
    ), 400


@app.errorhandler(exceptions.MalformedUserException)
def malformed_user_handler(e: exceptions.MalformedUserException):
    return send_template("exceptions/malformedUser.liquid"), 500


@app.errorhandler(exceptions.MalformedRequestException)
def malformed_req_handler(e: exceptions.MalformedRequestException):
    return send_template("exceptions/malformedReq.liquid"), 500


@app.errorhandler(exceptions.DocketNotVoting)
def docket_not_voting(e: exceptions.DocketNotVoting):
    return send_template('exceptions/notVoting.liquid'), 500

@app.errorhandler(TimeoutError)
def quick_post_handle(e: TimeoutError):
    return """You have submitted too many post requests in 10 seconds. 
    Please wait before submitting aditional requests.""", 500