from app import app
from src.utils import exceptions
from flask import session, request
from src.utils.templates import send_template

@app.errorhandler(404)
def page_not_found(e):
    return send_template('exceptions/404.liquid')

@app.errorhandler(500)
def page_not_found(e):
    return send_template('exceptions/500.liquid')

@app.errorhandler(exceptions.InvalidPermissionException)
def invalid_permission(e: exceptions.InvalidPermissionException):
    return send_template('exceptions/invalidPermissions.liquid')

@app.errorhandler(exceptions.UserNotSignedInException)
def return_user_sign_in_with_ref_url(e: exceptions.UserNotSignedInException):
    session['ref'] = request.path
    return send_template('login.liquid', heading="This page requires authorization to view. Please sign in to continue.")

@app.errorhandler(exceptions.UserNotFoundException)
def return_user_sign_in_not_found(e: exceptions.UserNotFoundException):
    return send_template('login.liquid', heading='Your username or password is incorrect, or your account is not active.')

@app.errorhandler(exceptions.MalformedUserException)
def malformed_user_handler(e: exceptions.MalformedUserException):
    return send_template('exceptions/malformedUser.liquid')

@app.errorhandler(exceptions.MalformedRequestException)
def malformed_req_handler(e: exceptions.MalformedRequestException):
    return send_template('exceptions/malformedReq.liquid')