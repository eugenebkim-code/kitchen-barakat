import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_receipt_image(file: UploadFile) -> str:
    """
    Saves uploaded receipt image to local storage directory and returns local relative path or URL.
    """
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"receipt_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    return f"/uploads/{filename}"
