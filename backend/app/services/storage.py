import os
import uuid
from fastapi import UploadFile

from app.core.config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
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


def delete_uploaded_file(public_path: str | None) -> None:
    """
    Removes a file previously returned by save_image()/save_receipt_image()
    (a "/uploads/<name>" public path) from disk, if it exists. Silently
    ignores missing files/paths outside our own uploads convention.
    """
    if not public_path or not public_path.startswith("/uploads/"):
        return
    filename = public_path[len("/uploads/"):]
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
