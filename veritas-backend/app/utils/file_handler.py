import os
import uuid
from fastapi import UploadFile, HTTPException
from pathlib import Path

UPLOAD_DIR = "./uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".pdf"]

def create_upload_dir():
    Path(UPLOAD_DIR).mkdir(exist_ok=True)

def validate_file(file: UploadFile):
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Check file size (this is basic check, real size checked during upload)
    return True

async def save_uploaded_file(file: UploadFile) -> tuple:
    validate_file(file)
    create_upload_dir()
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    file_size = 0
    with open(file_path, "wb") as buffer:
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)  # Clean up
            raise HTTPException(status_code=400, detail="File too large")
        
        buffer.write(content)
    
    return file_path, file_size