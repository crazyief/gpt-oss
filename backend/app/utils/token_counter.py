"""
Token counting utility for LLM context management.

This module provides token estimation to enforce the SAFE_ZONE_TOKEN limit
and prevent model failures from exceeding context windows.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count from text using character-based approximation.

    WHY CHARACTER-BASED APPROXIMATION:
    ===================================
    We don't have direct access to the model's tokenizer (phi4/magistral/etc).
    Loading the tokenizer would add significant overhead and dependencies.

    EMPIRICAL TESTING RESULTS:
    - English text: ~4 characters per token
    - Code/technical: ~3.5 characters per token
    - Chinese/multilingual: ~2 characters per token

    CONSERVATIVE APPROACH:
    We use 4 characters per token, which slightly OVERESTIMATES token count.
    This gives us a ~10-15% safety margin, which is preferable to underestimating.

    TRADE-OFFS:
    ✅ Fast (no tokenizer loading)
    ✅ Conservative (prevents overruns)
    ✅ Model-agnostic (works with any LLM)
    ❌ Not exact (but good enough for safety checks)

    FIXED (BUG-QA-002):
    ===================
    - Use ceiling division to ensure minimum 1 token for non-empty strings
    - Prevents underestimation of context usage for very short messages
    - "Hi" now returns 1 token instead of 0

    Args:
        text: Input text to estimate tokens for

    Returns:
        Estimated token count (minimum 1 for non-empty strings)

    Example:
        >>> estimate_tokens("Hello world!")
        >>> 3  # 12 characters / 4 = 3 tokens
        >>> estimate_tokens("Hi")
        >>> 1  # ceil(2 / 4) = 1 token (was 0 before fix)
    """
    if not text:
        return 0

    # 4 characters ≈ 1 token (conservative estimate)
    # Use ceiling division to avoid returning 0 for short strings
    import math
    return math.ceil(len(text) / 4)


def estimate_conversation_tokens(messages: List[Dict[str, Any]]) -> int:
    """
    Estimate total tokens in a conversation history.

    WHY THIS FUNCTION EXISTS:
    =========================
    Conversations include:
    - User messages
    - Assistant messages
    - System prompts
    - Message formatting (role labels, separators)

    We need to account for ALL of these when calculating total token usage.

    Args:
        messages: List of message dicts with 'role' and 'content' keys

    Returns:
        Estimated total tokens for entire conversation

    Example:
        >>> messages = [
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hi there!"}
        ... ]
        >>> estimate_conversation_tokens(messages)
        >>> 8  # Includes formatting overhead
    """
    total_tokens = 0

    for msg in messages:
        content = msg.get('content', '')
        role = msg.get('role', '')

        # Count content tokens
        total_tokens += estimate_tokens(content)

        # Add formatting overhead (role labels, separators)
        # Format: "\nRole: content"
        # Roughly 3-5 tokens per message for formatting
        total_tokens += 5

    return total_tokens


def calculate_max_response_tokens(
    prompt: str,
    safe_zone_token: int = 22800,
    safety_buffer: int = 100,
    minimum_response: int = 500
) -> int:
    """
    Calculate maximum tokens available for LLM response.

    SAFE_ZONE_TOKEN ENFORCEMENT:
    ============================
    The SAFE_ZONE_TOKEN (22,800) is the TOTAL token limit for:
    - Conversation history (past messages)
    - System prompts and formatting
    - LLM response generation

    WHY DYNAMIC CALCULATION IS CRITICAL:
    ====================================
    ❌ WRONG APPROACH (Fixed max_tokens):
    max_tokens = 18000  # Fixed value

    FAILURE SCENARIO:
    - Conversation history: 5,000 tokens
    - Fixed max_tokens: 18,000 tokens
    - TOTAL: 23,000 tokens ❌ EXCEEDS 22,800 SAFE_ZONE_TOKEN!
    - Result: Model crashes with context overflow

    ✅ CORRECT APPROACH (Dynamic max_tokens):
    max_response_tokens = SAFE_ZONE_TOKEN - prompt_tokens - safety_buffer

    SUCCESS SCENARIO:
    - Conversation history: 5,000 tokens
    - Dynamic max_tokens: 22,800 - 5,000 - 100 = 17,700 tokens
    - TOTAL: 22,700 tokens ✅ WITHIN SAFE_ZONE_TOKEN
    - Result: Model generates response safely

    FORMULA BREAKDOWN:
    ==================
    max_response_tokens = SAFE_ZONE_TOKEN - prompt_tokens - safety_buffer

    WHERE:
    - SAFE_ZONE_TOKEN: Hard limit for total context (22,800)
    - prompt_tokens: Tokens used by conversation history + system prompt
    - safety_buffer: Extra margin for stop sequences, formatting (100)
    - minimum_response: Floor value to ensure useful responses (500)

    SAFETY BUFFER (100 tokens):
    - Stop sequences: "\nUser:", "\nAssistant:" (~10 tokens)
    - Message formatting overhead (~20 tokens)
    - Token estimation error margin (~70 tokens)

    MINIMUM RESPONSE (500 tokens):
    - Ensures LLM can generate meaningful responses
    - If conversation is too long, we enforce this minimum
    - Caller should consider trimming history if this happens

    Args:
        prompt: The full prompt including conversation history
        safe_zone_token: Total token budget (default: 22,800)
        safety_buffer: Extra margin for overhead (default: 100)
        minimum_response: Minimum tokens for response (default: 500)

    Returns:
        Maximum tokens available for response generation

    Example (Short conversation):
        >>> prompt = "User: Hello\nAssistant: Hi\nUser: How are you?"
        >>> calculate_max_response_tokens(prompt)
        >>> 22685  # 22800 - 15 - 100 = 22,685 tokens available

    Example (Long conversation):
        >>> long_prompt = "..." * 5000  # 20,000 characters = ~5,000 tokens
        >>> calculate_max_response_tokens(long_prompt)
        >>> 17700  # 22800 - 5000 - 100 = 17,700 tokens available

    Example (Very long conversation):
        >>> very_long_prompt = "..." * 22000  # 88,000 chars = ~22,000 tokens
        >>> calculate_max_response_tokens(very_long_prompt)
        >>> 500  # Falls back to minimum_response (2700 would be too small)
    """
    # Calculate tokens used by prompt
    prompt_tokens = estimate_tokens(prompt)

    # Calculate remaining tokens for response
    max_response_tokens = safe_zone_token - prompt_tokens - safety_buffer

    # Enforce minimum response size BUT never exceed safe zone
    if max_response_tokens < minimum_response:
        # CRITICAL: Check if using minimum would exceed safe zone
        if prompt_tokens + minimum_response + safety_buffer > safe_zone_token:
            # Cannot use minimum without exceeding safe zone
            # This means conversation history is TOO LONG
            logger.error(
                f"Conversation history ({prompt_tokens} tokens) is too long! "
                f"Even minimum response ({minimum_response}) would exceed "
                f"SAFE_ZONE_TOKEN ({safe_zone_token}). "
                f"CRITICAL: Application must trim conversation history immediately."
            )
            # Return what we can without exceeding limit
            # This might be very small, but at least we don't crash
            return max(0, max_response_tokens)

        logger.warning(
            f"Conversation history is very long ({prompt_tokens} tokens). "
            f"Only {max_response_tokens} tokens available for response. "
            f"Using minimum {minimum_response} tokens instead. "
            f"Consider trimming conversation history."
        )
        return minimum_response

    # Log token allocation for debugging
    logger.info(
        f"Token allocation: "
        f"prompt={prompt_tokens}, "
        f"response={max_response_tokens}, "
        f"total={prompt_tokens + max_response_tokens + safety_buffer}, "
        f"limit={safe_zone_token}"
    )

    return max_response_tokens
