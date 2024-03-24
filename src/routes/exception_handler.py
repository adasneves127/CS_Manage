from app import app
from src.utils import exceptions
from flask import session, request
from src.utils.templates import send_template

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

@app.errorhandler(exceptions.InvalidPermissionException)
def invalid_permission(e: exceptions.InvalidPermissionException):
    return send_template('invalidPermissions.liquid')

@app.errorhandler(exceptions.UserNotSignedInException)
def return_user_sign_in_with_ref_url(e: exceptions.UserNotSignedInException):
    session['ref'] = request.path
    return send_template('login.liquid', heading="This page requires authorization to view. Please sign in to continue.")