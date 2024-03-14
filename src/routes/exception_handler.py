from app import app
from src.utils import exceptions

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

@app.errorhandler(exceptions.InvalidPermissionException)
def invalid_permission(e):
    return "Invalid permission", 403