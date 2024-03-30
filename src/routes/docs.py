from app import app
from flask import send_from_directory, send_file

@app.route("/docs/<path:path>")
def send_docs(path):
    print(path)
    return send_from_directory('interface/private/docs/', path)

@app.route('/docs/')
def send_docs_index():
    return send_file('interface/private/docs/index.html')