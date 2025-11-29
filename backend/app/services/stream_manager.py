"""
Stream manager for active SSE chat sessions.

Manages active streaming sessions, allowing cancellation and cleanup.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
import uuid

logger = logging.getLogger(__name__)


class StreamSession:
    """
    Represents an active streaming session.

    Tracks the asyncio task running the stream and metadata.
    """

    def __init__(self, session_id: str, task: asyncio.Task = None, data: dict = None):
        """
        Initialize a stream session.

        Args:
            session_id: Unique session identifier (UUID)
            task: Asyncio task running the stream (optional for data-only sessions)
            data: Session data dict (for two-step SSE flow)

        Note:
            session_id is generated with uuid.uuid4() for uniqueness.
            task is the asyncio.Task that's generating and yielding tokens.
            data stores conversation_id, message content for GET endpoint.
        """
        self.session_id = session_id
        self.task = task
        self.data = data or {}
        self.start_time = datetime.utcnow()
        self.cancelled = False

    def cancel(self) -> bool:
        """
        Cancel the streaming session.

        Returns:
            True if cancelled successfully, False if already done/cancelled

        Note:
            This calls asyncio.Task.cancel() which raises CancelledError
            in the task. The task's exception handler should catch this
            and clean up gracefully.

        FIXED (BUG-QA-003):
            Added None check for task before calling task.done()
            Prevents AttributeError for data-only sessions (two-step SSE flow)
        """
        # Check if task exists (might be None for data-only sessions)
        if self.task is None:
            logger.warning(f"Cannot cancel session {self.session_id}: No task associated")
            return False

        if self.task.done() or self.cancelled:
            return False

        # Cancel the task
        # WHY cancel(): This is the standard asyncio way to stop a task.
        # It raises CancelledError in the task, allowing graceful cleanup.
        self.task.cancel()
        self.cancelled = True

        logger.info(f"Cancelled stream session: {self.session_id}")
        return True


class StreamManager:
    """
    Manages active streaming sessions.

    Provides thread-safe storage and retrieval of active streams,
    allowing cancellation and automatic cleanup.
    """

    def __init__(self):
        """
        Initialize stream manager.

        Creates empty dict for active sessions.
        WHY dict not list: O(1) lookup by session_id for cancellation.
        """
        # Active sessions indexed by session_id
        # WHY session_id as key: Allows fast lookup when client requests cancellation
        self._sessions: Dict[str, StreamSession] = {}

        # Lock for thread-safe access
        # WHY lock: Multiple concurrent requests could modify _sessions dict.
        # asyncio.Lock ensures only one coroutine accesses it at a time.
        self._lock = asyncio.Lock()

    async def create_session(self, task: asyncio.Task) -> str:
        """
        Create and register a new streaming session.

        Args:
            task: Asyncio task running the stream

        Returns:
            session_id (UUID string)

        Note:
            Generates a UUID v4 for the session ID to ensure uniqueness.
            WHY UUID: Prevents collisions even with thousands of concurrent sessions.
        """
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create session object
        session = StreamSession(session_id, task)

        # Register session (thread-safe)
        async with self._lock:
            self._sessions[session_id] = session

        logger.info(f"Created stream session: {session_id}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[StreamSession]:
        """
        Get a streaming session by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            StreamSession or None if not found

        Note:
            Returns None for completed or invalid session IDs.
        """
        async with self._lock:
            return self._sessions.get(session_id)

    async def cancel_session(self, session_id: str) -> bool:
        """
        Cancel a streaming session.

        Args:
            session_id: Session ID to cancel

        Returns:
            True if cancelled successfully, False if not found or already done

        Note:
            This calls cancel() on the session's task, which raises
            CancelledError in the streaming coroutine.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.warning(f"Session not found for cancellation: {session_id}")
                return False

            return session.cancel()

    async def cleanup_session(self, session_id: str) -> None:
        """
        Remove a session from the active sessions dict.

        Args:
            session_id: Session ID to clean up

        Note:
            Called when a stream completes (normally or via cancellation).
            WHY separate method: Allows caller to control when cleanup happens.
            This is called in the finally block of the streaming endpoint.
        """
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"Cleaned up stream session: {session_id}")

    async def cleanup_completed_sessions(self) -> int:
        """
        Clean up all completed sessions.

        Returns:
            Number of sessions cleaned up

        Note:
            This is a maintenance operation that can be called periodically
            to remove completed sessions that weren't properly cleaned up.
            WHY needed: If a client disconnects abruptly, the session might
            not be cleaned up in the finally block. This prevents memory leaks.

        FIXED (MEDIUM-005):
            Added None check for session.task before calling task.done()
            Prevents AttributeError for data-only sessions (two-step SSE flow)
        """
        cleanup_count = 0
        async with self._lock:
            # Find completed sessions
            # SECURITY FIX: Check if task exists before calling done()
            # Data-only sessions (from POST /stream) have task=None
            completed_ids = [
                sid for sid, session in self._sessions.items()
                if session.task and session.task.done()
            ]

            # Remove them
            for sid in completed_ids:
                del self._sessions[sid]
                cleanup_count += 1

        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} completed sessions")

        return cleanup_count

    async def get_active_count(self) -> int:
        """
        Get count of active streaming sessions.

        Returns:
            Number of currently active sessions

        Note:
            Useful for monitoring and capacity planning.
            If this number grows very large (>1000), it might indicate
            a resource leak or DoS attack.
        """
        async with self._lock:
            return len(self._sessions)

    async def create_stream_session(self, data: dict) -> str:
        """
        Create a stream session with data (for two-step SSE flow).

        Args:
            data: Session data (conversation_id, user_message, message_ids, etc.)

        Returns:
            session_id (UUID string)

        Note:
            This is used for the POST /api/chat/stream endpoint which creates
            the session and returns the session_id. The GET /api/chat/stream/{id}
            endpoint then retrieves this data to start streaming.
        """
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create session object with data (no task yet)
        session = StreamSession(session_id, task=None, data=data)

        # Register session (thread-safe)
        async with self._lock:
            self._sessions[session_id] = session

        logger.info(f"Created stream session with data: {session_id}")
        return session_id

    async def get_stream_session(self, session_id: str) -> Optional[dict]:
        """
        Get stream session data by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session data dict or None if not found

        Note:
            Used by GET /api/chat/stream/{session_id} to retrieve the
            conversation_id and message needed to start streaming.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            return session.data if session else None

    async def cleanup_stream_session(self, session_id: str) -> None:
        """
        Alias for cleanup_session for consistency with new method names.

        Args:
            session_id: Session ID to clean up
        """
        await self.cleanup_session(session_id)


# Singleton instance for dependency injection
# WHY singleton: StreamManager is a global registry of active sessions.
# Having multiple instances would defeat the purpose (can't cancel sessions
# registered in a different instance).
stream_manager = StreamManager()
