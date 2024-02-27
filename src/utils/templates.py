
from flask_liquid import render_template
from app import app
from src.utils.app_utils import load_app_info

def send_template(template: str, **kwargs):
    with app.app_context():
        app_info = load_app_info()
        return render_template(template, **app_info, **kwargs)