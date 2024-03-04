from flask import session
from src.utils.app_utils import load_app_info
from src.utils.db_utils import connect
from src.utils.constructors.emails import password_reset_email
from src.utils.templates import send_template

def get_session_user():
    pass