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
import logging
from typing import Optional
from pathlib import Path

# SECURITY FIX (SEC-H02): Magic library availability flag
# WHY lazy import: python-magic can segfault on systems without libmagic installed
# at import time (before try/except can catch it). Lazy import inside the function
# allows the module to load successfully even without libmagic.
MAGIC_AVAILABLE = None  # Will be set on first use

logger = logging.getLogger(__name__)


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


def validate_file_content_type(file_path: str, expected_mime: str) -> tuple[bool, Optional[str]]:
    """
    SECURITY FIX (SEC-H02): Validate file content type using magic bytes.

    WHY THIS IS CRITICAL:
    - Browser-provided Content-Type headers can be trivially spoofed by attackers
    - Attackers can upload malicious executables (.exe, .sh, .bat) with fake .pdf extension
    - File extensions alone are insufficient (can be renamed: malware.exe → malware.pdf)
    - Magic bytes detection reads actual file header to determine true file type

    ATTACK SCENARIO WITHOUT THIS CHECK:
    1. Attacker creates malicious executable: virus.exe
    2. Renames it to: report.pdf
    3. Sets Content-Type: application/pdf in upload request
    4. Our validation checks extension (.pdf ✓) and MIME type (application/pdf ✓)
    5. File gets uploaded to server and could be executed later

    WITH THIS CHECK:
    - Magic bytes detector reads file header: MZ (Windows executable signature)
    - Detected type: application/x-dosexec
    - Expected type: application/pdf
    - Validation FAILS → Upload rejected

    Args:
        file_path: Path to the uploaded file on disk
        expected_mime: MIME type we expect (from header validation)

    Returns:
        Tuple of (is_valid, error_message)
        Success: (True, None)
        Failure: (False, "Detailed error message")

    Examples:
        validate_file_content_type("/tmp/file.pdf", "application/pdf")
        → (True, None) if file is actually a PDF

        validate_file_content_type("/tmp/file.pdf", "application/pdf")
        → (False, "File content type mismatch...") if file is actually an executable

    Security Notes:
        - This function requires python-magic and libmagic to be installed
        - If magic is unavailable, function logs warning and allows upload (degraded security)
        - Magic byte detection is NOT 100% foolproof but significantly raises the bar
        - Some file types (e.g., plain text) have no magic bytes and may be misdetected
    """
    global MAGIC_AVAILABLE

    # Lazy import magic library to avoid segfault on systems without libmagic
    if MAGIC_AVAILABLE is None:
        try:
            import magic as _magic
            # Test that it actually works
            _magic.from_buffer(b"test", mime=True)
            MAGIC_AVAILABLE = True
            logger.info("python-magic loaded successfully for content-based file validation")
        except Exception as e:
            MAGIC_AVAILABLE = False
            logger.warning(
                f"python-magic not available ({e}). Content-based file type validation disabled. "
                f"Install with: pip install python-magic python-magic-bin"
            )

    if not MAGIC_AVAILABLE:
        # SECURITY DEGRADATION: If magic library unavailable, log warning but allow upload
        # This prevents breaking uploads entirely if dependency is missing
        # Production systems SHOULD have python-magic installed
        logger.warning(
            f"SECURITY WARNING: python-magic not available. "
            f"Skipping content-based validation for {file_path}. "
            f"This reduces security against file type spoofing attacks."
        )
        return True, None

    try:
        import magic
        # Detect actual MIME type from file content (magic bytes)
        detected_mime = magic.from_file(file_path, mime=True)

        # Compare detected type with expected type
        if detected_mime != expected_mime:
            # SECURITY: Log detailed mismatch for forensics
            logger.warning(
                f"File type mismatch detected for {file_path}: "
                f"expected={expected_mime}, detected={detected_mime}. "
                f"Possible file type spoofing attack."
            )
            return False, (
                f"File content type mismatch: expected {expected_mime}, "
                f"but file appears to be {detected_mime}. "
                f"This may indicate a security issue."
            )

        # Success: File content matches expected type
        logger.debug(f"Content validation passed for {file_path}: {detected_mime}")
        return True, None

    except Exception as e:
        # Handle errors gracefully (corrupted file, I/O error, etc.)
        logger.error(f"Failed to detect file type for {file_path}: {str(e)}")
        return False, f"Failed to validate file content type: {str(e)}"
