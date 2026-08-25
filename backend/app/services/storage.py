import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_image(file: UploadFile, prefix: str) -> str:
    """
    Saves an uploaded image to local storage directory and returns its public path.
    """
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{prefix}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    return f"/uploads/{filename}"


async def save_receipt_image(file: UploadFile) -> str:
    return await save_image(file, "receipt")
