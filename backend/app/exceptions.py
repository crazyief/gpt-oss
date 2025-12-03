"""
Custom exception classes for GPT-OSS backend.

Provides structured error responses with error codes for better client-side handling.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class GPTOSSException(HTTPException):
    """
    Base exception class for all GPT-OSS errors.

    Extends FastAPI's HTTPException with error codes and structured details.
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize structured exception.

        Args:
            status_code: HTTP status code
            error_code: Machine-readable error code (e.g., "PROJECT_NOT_FOUND")
            message: Human-readable error message
            details: Optional additional context for debugging
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}

        # Create structured detail for FastAPI
        detail = {
            "error_code": error_code,
            "message": message,
            "details": self.details
        }

        super().__init__(status_code=status_code, detail=detail)


# ============================================================================
# Resource Not Found Errors (404)
# ============================================================================

class ProjectNotFoundError(GPTOSSException):
    """Raised when a project is not found or is soft-deleted."""

    def __init__(self, project_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PROJECT_NOT_FOUND",
            message=f"Project with ID {project_id} not found. It may have been deleted.",
            details={"project_id": project_id}
        )


class ConversationNotFoundError(GPTOSSException):
    """Raised when a conversation is not found or is soft-deleted."""

    def __init__(self, conversation_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CONVERSATION_NOT_FOUND",
            message=f"Conversation with ID {conversation_id} not found. It may have been deleted.",
            details={"conversation_id": conversation_id}
        )


class DocumentNotFoundError(GPTOSSException):
    """Raised when a document is not found."""

    def __init__(self, document_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="DOCUMENT_NOT_FOUND",
            message=f"Document with ID {document_id} not found.",
            details={"document_id": document_id}
        )


class StreamSessionNotFoundError(GPTOSSException):
    """Raised when a stream session is not found or expired."""

    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="STREAM_SESSION_NOT_FOUND",
            message=f"Stream session not found. It may have expired or been cancelled.",
            details={"session_id": session_id}
        )


# ============================================================================
# Validation Errors (400)
# ============================================================================

class ValidationError(GPTOSSException):
    """Raised when request validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {}
        if field:
            details["field"] = field

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )


class FileValidationError(GPTOSSException):
    """Raised when file upload validation fails."""

    def __init__(self, filename: str, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_VALIDATION_ERROR",
            message=f"File '{filename}' validation failed: {reason}",
            details={"filename": filename, "reason": reason}
        )


# ============================================================================
# Service Errors (500/503)
# ============================================================================

class DatabaseError(GPTOSSException):
    """Raised when a database operation fails."""

    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message=f"Database operation failed: {operation}. Please try again.",
            details=details or {"operation": operation}
        )


class LLMServiceError(GPTOSSException):
    """Raised when LLM service communication fails."""

    def __init__(self, message: str, llm_url: Optional[str] = None):
        details = {}
        if llm_url:
            details["llm_url"] = llm_url

        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="LLM_SERVICE_ERROR",
            message=f"LLM service error: {message}",
            details=details
        )


class LLMTimeoutError(GPTOSSException):
    """Raised when LLM service times out."""

    def __init__(self, timeout_seconds: int):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_code="LLM_TIMEOUT",
            message=f"LLM service timed out after {timeout_seconds} seconds. Please try a shorter message or try again later.",
            details={"timeout_seconds": timeout_seconds}
        )


class FileSystemError(GPTOSSException):
    """Raised when file system operation fails."""

    def __init__(self, operation: str, file_path: Optional[str] = None):
        details = {"operation": operation}
        if file_path:
            details["file_path"] = file_path

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="FILE_SYSTEM_ERROR",
            message=f"File system operation failed: {operation}. Please try again.",
            details=details
        )


# ============================================================================
# Helper Functions
# ============================================================================

def handle_database_error(operation: str, exception: Exception) -> None:
    """
    Convert database exceptions to structured DatabaseError.

    SECURITY: Internal exception details are logged but NOT exposed to API responses.
    This prevents information leakage that could aid attackers.

    Args:
        operation: Description of what failed (e.g., "create project")
        exception: The caught exception

    Raises:
        DatabaseError: Always raises with sanitized error (no internal details)
    """
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    # Log full details internally for debugging
    logger.error(f"Database error during {operation}: {exception}")
    logger.error(traceback.format_exc())

    # SECURITY FIX: Do NOT expose internal exception details to client
    # Attackers can use this info for reconnaissance (SQL injection, path traversal)
    raise DatabaseError(
        operation=operation,
        details={}  # Empty - never expose internal details to API response
    )
