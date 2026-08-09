import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_secure_filepath(upload_folder, original_filename):
    """
    Generates a secure UUID-prefixed file path to prevent directory traversal
    and overwrite attacks. Never trusts raw filenames.
    """
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = "resume.pdf"
    
    extension = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else 'pdf'
    unique_filename = f"{uuid.uuid4().hex}_{safe_name}"
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
        
    full_path = os.path.join(upload_folder, unique_filename)
    return full_path, unique_filename

def validate_pdf_file(file_path):
    """
    Validates PDF file magic headers to ensure it is a valid PDF and not a malicious file.
    """
    if not os.path.exists(file_path):
        return False, "File does not exist on server."
        
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                return False, "Uploaded file is not a valid PDF document."
        return True, ""
    except Exception as e:
        return False, f"Failed to read file header: {str(e)}"
