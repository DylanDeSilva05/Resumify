"""
File handling utilities
"""
import os
import hashlib
import mimetypes
from typing import Optional
from pathlib import Path

from app.core.config import settings


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower().lstrip('.')


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    extension = get_file_extension(filename)
    return extension in settings.ALLOWED_EXTENSIONS


def get_file_mime_type(filename: str) -> Optional[str]:
    """Get MIME type of file"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def generate_file_hash(file_path: str) -> str:
    """Generate SHA-256 hash of file content"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def get_safe_filename(filename: str) -> str:
    """Generate safe filename by removing dangerous characters"""
    # Remove path components
    filename = os.path.basename(filename)

    # Replace dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext

    return filename


def ensure_upload_directory():
    """Ensure upload directory exists"""
    upload_dir = Path(settings.UPLOAD_FOLDER)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir