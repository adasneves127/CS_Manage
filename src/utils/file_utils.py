import subprocess
import tempfile
import base64
from flask import current_app

# A list of valid files that can be uploaded to the system

valid_file_types = [
    #   ('Type Command Output',         '.extention'),
    ("PDF document", ".pdf"),
    ("RFC 822 mail", ".eml"),
    ("OpenDocument Text", ".odt"),
    ("OpenDocument Presentation", ".odp"),
    ("OpenDocument Spreadsheet", ".ods"),
    ("ASCII text", ".txt"),
    ("JPEG image data", ".jpg"),
    ("JPEG image data", ".jpeg"),
    ("PNG image data", ".png"),
    ("GIF image data", ".gif"),
]


def is_file_valid_type(file_name: str, file_data: str) -> bool:

    # Write the file_data to a file
    temp_file_path = ""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(base64.b64decode(file_data))
        temp_file_path = temp_file.name

    proc = subprocess.Popen(["/bin/file", "-b", temp_file_path],
                            stdout=subprocess.PIPE)
    output = proc.stdout.read().decode()
    return any([output.startswith(x[0]) for x in valid_file_types])