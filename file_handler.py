# file_handler.py
from werkzeug.utils import secure_filename
import os

import os

def handle_upload(file, upload_folder):
    filename = secure_filename(file.filename)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file.save(os.path.join(upload_folder, filename))
    return filename