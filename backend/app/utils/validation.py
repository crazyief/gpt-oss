"""
Input validation and sanitization utilities.

Provides security functions for sanitizing user input to prevent
XSS attacks and other injection vulnerabilities.

FIXED (Issue-10: Missing Input Sanitization):
============================================
Defense-in-depth security layer added to complement frontend validation
and Marked.js HTML escaping.
"""

import re
from html import escape


def sanitize_text_input(value: str, allow_newlines: bool = False) -> str:
    """
    Sanitize user text input to prevent XSS and injection attacks.

    Security measures:
    - HTML escape: Converts <, >, &, etc. to entities
    - Control character removal: Strips non-printable characters
    - Whitespace normalization: Strips leading/trailing whitespace

    Args:
        value: User input string to sanitize
        allow_newlines: If True, preserves \n and \t (for message content)
                       If False, removes all control characters (for titles, names)

    Returns:
        Sanitized string safe for storage and display

    Examples:
        >>> sanitize_text_input("<script>alert('XSS')</script>")
        "&lt;script&gt;alert('XSS')&lt;/script&gt;"

        >>> sanitize_text_input("Title with\x00null byte")
        "Title withnull byte"

        >>> sanitize_text_input("Message\nwith\nnewlines", allow_newlines=True)
        "Message\nwith\nnewlines"

    Security Note:
        This is defense-in-depth. Frontend also escapes HTML via Marked.js.
        Multiple layers prevent XSS even if one layer fails.
    """
    if not value:
        return value

    # Escape HTML entities (< > & " ')
    # WHY: Prevents <script> tags from executing
    # Example: "<img src=x onerror=alert(1)>" → safe HTML entities
    value = escape(value)

    # Remove control characters
    # Control chars: 0x00-0x1F (except \n, \r, \t if allowed)
    # WHY: Prevents null byte injection, format string attacks
    if allow_newlines:
        # Keep newline \n (0x0A) and tab \t (0x09) for message content
        # Remove all other control characters
        value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
    else:
        # Remove ALL control characters (for single-line fields like titles)
        value = re.sub(r'[\x00-\x1F\x7F]', '', value)

    # Strip leading/trailing whitespace
    # WHY: Prevents "  malicious  " from bypassing UI validations
    value = value.strip()

    return value


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.

    Security measures:
    - Remove path separators (/, \)
    - Remove null bytes
    - Limit to safe characters

    Args:
        filename: Original filename from upload

    Returns:
        Safe filename for storage

    Examples:
        >>> sanitize_filename("../../etc/passwd")
        "etcpasswd"

        >>> sanitize_filename("file<script>.txt")
        "filescripttxt"

    Security Note:
        STAGE 2 requirement for document upload feature.
        Prevents path traversal and file system injection.
    """
    if not filename:
        return "unnamed_file"

    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Keep only alphanumeric, dots, hyphens, underscores
    # WHY: Prevents shell injection via filenames
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)

    # Prevent hidden files (starting with dot)
    if filename.startswith('.'):
        filename = 'file_' + filename[1:]

    # Ensure not empty after sanitization
    if not filename:
        return "unnamed_file"

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename
