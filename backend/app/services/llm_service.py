"""
LLM service for integration with llama.cpp inference server.

Handles communication with the llama.cpp HTTP API for text generation,
including streaming responses and error handling.
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service class for LLM (Large Language Model) operations.

    Manages communication with llama.cpp server for text generation.
    Supports both streaming and non-streaming completions.
    """

    def __init__(self):
        """
        Initialize LLM service.

        Sets up HTTP client with timeout configuration.
        WHY async client: llama.cpp can take 10-60 seconds to generate responses,
        so we need async I/O to avoid blocking the event loop. This allows
        FastAPI to handle other requests while waiting for LLM responses.
        """
        # HTTP client configuration
        # WHY specific timeouts: llama.cpp can take up to 60s for long responses.
        # connect=5s: Fast failure if server is down
        # read=60s: Allow time for generation
        # write=5s: Sending prompts should be fast
        # pool=10s: Connection pool management
        self.timeout = httpx.Timeout(
            connect=5.0,
            read=60.0,
            write=5.0,
            pool=10.0
        )

        # Base URL for llama.cpp server
        # WHY from settings: Allows different URLs for dev/staging/prod.
        # In docker-compose, this is http://llama:8080
        self.llm_url = settings.LLM_API_URL

    async def health_check(self) -> bool:
        """
        Check if LLM service is available.

        Returns:
            True if service is healthy, False otherwise

        Note:
            This makes a lightweight request to verify connectivity.
            Used by the /health endpoint to report service status.
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                # llama.cpp has a /health endpoint (or we use /completion with empty prompt)
                # WHY quick timeout: Health checks should fail fast (5s max)
                response = await client.get(f"{self.llm_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stop_sequences: Optional[list[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate text with streaming response.

        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate (default: 2048)
            temperature: Sampling temperature 0-1 (default: 0.7)
            stop_sequences: Optional list of sequences that stop generation

        Yields:
            Individual tokens as they are generated

        Raises:
            httpx.HTTPStatusError: If LLM service returns error status
            httpx.TimeoutException: If generation takes >60 seconds
            Exception: For other network/parsing errors

        Note:
            This uses SSE (Server-Sent Events) protocol to stream tokens.
            WHY streaming: For long responses (500+ tokens), streaming provides
            better UX - users see partial responses immediately rather than
            waiting 30+ seconds for complete generation.
        """
        # Build request payload
        # WHY these parameters:
        # - stream=true: Enable token-by-token streaming
        # - n_predict=max_tokens: Limit generation length
        # - temperature: Controls randomness (0.7 is balanced for knowledge Q&A)
        # - stop: Prevents infinite generation
        payload = {
            "prompt": prompt,
            "stream": True,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stop": stop_sequences or [],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Stream response using async with
                # WHY POST /completion: This is llama.cpp's standard endpoint
                async with client.stream(
                    "POST",
                    f"{self.llm_url}/completion",
                    json=payload
                ) as response:
                    # Check response status before consuming stream
                    response.raise_for_status()

                    # Process streaming response
                    # WHY async for: Processes chunks as they arrive without
                    # buffering the entire response in memory
                    async for chunk in response.aiter_lines():
                        if not chunk:
                            continue

                        # Parse JSON from each line
                        # llama.cpp returns: {"content": "token", "stop": false}
                        try:
                            # Remove "data: " prefix if present (SSE format)
                            if chunk.startswith("data: "):
                                chunk = chunk[6:]

                            # Skip SSE comments and empty lines
                            if not chunk or chunk.startswith(":"):
                                continue

                            # Parse JSON
                            import json
                            data = json.loads(chunk)

                            # Extract token content
                            # WHY check 'content': llama.cpp may send metadata events
                            # without content (e.g., stop events, timing info)
                            if "content" in data and data["content"]:
                                yield data["content"]

                            # Check if generation stopped
                            if data.get("stop", False):
                                break

                        except json.JSONDecodeError as e:
                            # Log but don't crash on parse errors
                            # WHY continue: One malformed chunk shouldn't kill the stream
                            logger.warning(f"Failed to parse LLM response chunk: {e}")
                            continue

        except httpx.TimeoutException:
            logger.error("LLM request timed out after 60 seconds")
            raise Exception("LLM service timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM service returned error: {e.response.status_code}")
            if e.response.status_code == 503:
                raise Exception("LLM service unavailable")
            raise Exception(f"LLM service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def generate_complete(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stop_sequences: Optional[list[str]] = None
    ) -> str:
        """
        Generate text and return complete response.

        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop_sequences: Optional stop sequences

        Returns:
            Complete generated text as string

        Note:
            This uses the same streaming endpoint but collects all tokens.
            WHY reuse stream: Avoids duplicating LLM communication logic.
            For non-streaming use cases, this is simpler than handling SSE.
        """
        # Collect all tokens from stream
        tokens = []
        async for token in self.generate_stream(
            prompt, max_tokens, temperature, stop_sequences
        ):
            tokens.append(token)

        return "".join(tokens)

    def build_chat_prompt(self, messages: list[dict]) -> str:
        """
        Build a chat prompt from conversation history with system instructions.

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            Formatted prompt string for the LLM with system instructions

        Note:
            This formats messages into llama.cpp's expected chat template with
            comprehensive markdown formatting guidelines.

            WHY system prompt: Ensures consistent, well-formatted responses with
            proper code formatting, inline code backticks, and markdown structure.

        Example:
            [
                {"role": "user", "content": "How to print hello world in Python?"}
            ]

            Becomes:
            System: [formatting instructions]

            User: How to print hello world in Python?

            Assistant:
        """
        # System prompt with markdown formatting guidelines
        # WHY detailed formatting rules: Ensures LLM outputs proper markdown
        # that renders correctly in frontend (inline code, code blocks, lists, etc.)
        system_prompt = """You are a helpful AI assistant. Follow these formatting rules:

**Code Formatting (CRITICAL)**:

1. **Inline code (single backticks `)**:
   - Use for: function names, variable names, commands, file names, single-line code
   - Examples:
     ✅ "Use the `print()` function"
     ✅ "Run `npm install` command"
     ✅ "The code `print("hello world")` will output hello world"
     ✅ "Set `x = 5`"
     ✅ "The result is `42`"

2. **Code blocks (triple backticks ```)**:
   - ONLY use for multi-line code examples or complete programs
   - DO NOT use for single-line code - use inline code instead
   - Example when to use:
     ✅ Multi-line function definition
     ✅ Complete program with multiple lines
     ✅ Multiple related code statements

**When to use inline code vs code blocks**:
- Single line code → Use inline: `print("hello")`
- 2-3 lines → Still use inline if related: `x = 5`, `y = 10`
- 4+ lines or complete function → Use code block with ```

**Examples of CORRECT formatting**:
✅ "To print hello world, use `print("hello world")`"
✅ "Run `npm install` to install dependencies"
✅ "The answer is `42`"
✅ "Create a file named `config.json`"

**Examples of INCORRECT formatting**:
❌ Using code block for single line: ```print("hello")```
❌ Missing backticks: "Use the print() function"
❌ Missing backticks for numbers: "The result is 42"

Be helpful, accurate, and concise."""

        # Format conversation history
        formatted = [f"System: {system_prompt}"]

        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted.append(f"{role}: {content}")

        # Join with double newlines for clarity
        prompt = "\n\n".join(formatted)

        # CRITICAL: Add "Assistant:" prompt if the last message was from user
        # This signals the LLM to start generating the assistant's response
        if messages and messages[-1]["role"] == "user":
            prompt += "\n\nAssistant:"

        return prompt


# Singleton instance for dependency injection
# WHY singleton: LLM service is stateless and doesn't need multiple instances.
# This saves memory and allows connection pooling in the HTTP client.
llm_service = LLMService()
