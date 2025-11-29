"""
Document validation utilities.

Security-focused validation for file uploads including:
- Filename sanitization (path traversal prevention)
- MIME type validation
- File extension checking
- Safe filename generation
"""

import os
import re
import uuid
from typing import Optional
from pathlib import Path


# Configuration constants
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB in bytes
UPLOAD_BASE_DIR = "uploads"

# Allowed MIME types and extensions
# WHY this mapping: Validates both MIME type (from browser) and extension
# (from filename) to prevent file type spoofing attacks.
ALLOWED_TYPES = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/plain": [".txt"],
    "text/markdown": [".md"],
}


def get_allowed_extensions() -> list[str]:
    """Get flat list of all allowed file extensions."""
    return [ext for exts in ALLOWED_TYPES.values() for ext in exts]


def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
    """
    Validate and sanitize filename for security.

    SECURITY CHECKS:
    - Reject path traversal attempts (../, ..\, absolute paths)
    - Reject null bytes (filesystem injection)
    - Reject control characters (terminal injection)
    - Check extension is allowed

    Args:
        filename: Original filename from upload

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, "Error description")

    Examples:
        validate_filename("report.pdf") → (True, None)
        validate_filename("../etc/passwd") → (False, "Illegal path characters")
        validate_filename("file\x00.pdf") → (False, "Null byte detected")
    """
    # Check for null bytes (filesystem injection)
    if "\x00" in filename:
        return False, "Null byte detected in filename"

    # Check for path traversal attempts
    # WHY this regex: Catches ../, ..\, /../, \..\, and absolute paths
    if re.search(r'(\.\.[/\\]|^[/\\]|^[A-Za-z]:)', filename):
        return False, "Illegal path characters in filename"

    # Check for control characters (ASCII 0-31, 127)
    # WHY: Prevents terminal injection and filename display corruption
    if re.search(r'[\x00-\x1f\x7f]', filename):
        return False, "Control characters in filename"

    # Extract extension
    ext = Path(filename).suffix.lower()

    # Check extension is allowed
    if ext not in get_allowed_extensions():
        return False, f"File type not allowed: {ext}"

    return True, None


def validate_mime_type(mime_type: str, filename: str) -> tuple[bool, Optional[str]]:
    """
    Validate MIME type matches file extension.

    SECURITY: Prevents file type spoofing where malicious files
    claim to be safe types via MIME type.

    Args:
        mime_type: Content-Type from upload
        filename: Original filename

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        validate_mime_type("application/pdf", "doc.pdf") → (True, None)
        validate_mime_type("application/pdf", "doc.exe") → (False, "Extension mismatch")
    """
    # Check MIME type is allowed
    if mime_type not in ALLOWED_TYPES:
        return False, f"MIME type not allowed: {mime_type}"

    # Extract extension
    ext = Path(filename).suffix.lower()

    # Check extension matches MIME type
    allowed_extensions = ALLOWED_TYPES[mime_type]
    if ext not in allowed_extensions:
        return False, f"MIME type {mime_type} does not match extension {ext}"

    return True, None


def generate_safe_filename(original_filename: str) -> str:
    """
    Generate safe filename with UUID prefix.

    WHY UUID prefix: Prevents filename collisions and makes filenames
    unpredictable (security through obscurity for direct access attempts).

    Args:
        original_filename: User's original filename

    Returns:
        Safe filename with UUID prefix (e.g., "abc123-def456_report.pdf")

    Example:
        generate_safe_filename("report.pdf") → "abc123-def456_report.pdf"
    """
    # Generate UUID
    file_uuid = str(uuid.uuid4())

    # Sanitize original filename (remove any remaining path separators)
    safe_original = os.path.basename(original_filename)

    # Combine: uuid_originalname
    return f"{file_uuid}_{safe_original}"


def validate_file_size(file_size: int) -> tuple[bool, Optional[str]]:
    """
    Validate file size is within limits.

    Args:
        file_size: Size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large: {file_size} bytes exceeds {MAX_FILE_SIZE} bytes limit"
    return True, None
