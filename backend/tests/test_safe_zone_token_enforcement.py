"""
Test suite for SAFE_ZONE_TOKEN enforcement.

Verifies that the dynamic max_tokens calculation correctly prevents
context overflow by respecting the 22,800 token hard limit.
"""

import pytest
from app.utils.token_counter import (
    estimate_tokens,
    estimate_conversation_tokens,
    calculate_max_response_tokens
)


class TestTokenEstimation:
    """Test token estimation functions."""

    def test_estimate_tokens_empty_string(self):
        """Test that empty strings return 0 tokens."""
        assert estimate_tokens("") == 0

    def test_estimate_tokens_simple_text(self):
        """Test token estimation for simple English text."""
        # "Hello world!" = 12 characters / 4 = 3 tokens
        text = "Hello world!"
        tokens = estimate_tokens(text)
        assert tokens == 3

    def test_estimate_tokens_longer_text(self):
        """Test token estimation for longer text."""
        # 400 characters should be ~100 tokens
        text = "a" * 400
        tokens = estimate_tokens(text)
        assert tokens == 100

    def test_estimate_tokens_conservative(self):
        """
        Verify that estimation is conservative (overestimates).

        WHY: We use 4 chars/token which is conservative for English.
        This prevents underestimation that could exceed SAFE_ZONE_TOKEN.
        """
        # Typical English text is ~4-5 chars/token
        # Our estimate should be on the safe side
        text = "The quick brown fox jumps over the lazy dog"
        estimated = estimate_tokens(text)
        # 43 chars / 4 = 10 tokens (integer division)
        assert estimated == 10

    def test_estimate_conversation_tokens_empty(self):
        """Test empty conversation history."""
        messages = []
        tokens = estimate_conversation_tokens(messages)
        assert tokens == 0

    def test_estimate_conversation_tokens_single_message(self):
        """Test single message in conversation."""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        tokens = estimate_conversation_tokens(messages)
        # "Hello" = 5 chars / 4 = 1 token
        # + 5 tokens formatting overhead
        # = 6 tokens total
        assert tokens == 6

    def test_estimate_conversation_tokens_multi_message(self):
        """Test multiple messages in conversation."""
        messages = [
            {"role": "user", "content": "What is IEC 62443?"},
            {"role": "assistant", "content": "IEC 62443 is a cybersecurity standard."},
            {"role": "user", "content": "Tell me more about CR 2.11"}
        ]
        tokens = estimate_conversation_tokens(messages)

        # Message 1: 18 chars / 4 = 4 tokens + 5 overhead = 9
        # Message 2: 42 chars / 4 = 10 tokens + 5 overhead = 15
        # Message 3: 28 chars / 4 = 7 tokens + 5 overhead = 12
        # Total: 34 tokens (adjusted for actual character counts)
        assert tokens == 34


class TestMaxResponseTokens:
    """Test dynamic max_tokens calculation."""

    def test_short_conversation(self):
        """
        Test max_tokens calculation for short conversation.

        Scenario: User just started chatting, minimal history
        Expected: Should allow near-maximum response tokens
        """
        # 100 character prompt = 25 tokens
        prompt = "a" * 100
        max_tokens = calculate_max_response_tokens(
            prompt=prompt,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Expected: 22800 - 25 - 100 = 22,675 tokens
        assert max_tokens == 22675

    def test_medium_conversation(self):
        """
        Test max_tokens calculation for medium conversation.

        Scenario: Conversation with ~5,000 tokens of history
        Expected: Should reduce response tokens proportionally
        """
        # 20,000 character prompt = 5,000 tokens
        prompt = "a" * 20000
        max_tokens = calculate_max_response_tokens(
            prompt=prompt,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Expected: 22800 - 5000 - 100 = 17,700 tokens
        assert max_tokens == 17700

    def test_long_conversation(self):
        """
        Test max_tokens calculation for long conversation.

        Scenario: Conversation with ~15,000 tokens of history
        Expected: Should significantly reduce response tokens
        """
        # 60,000 character prompt = 15,000 tokens
        prompt = "a" * 60000
        max_tokens = calculate_max_response_tokens(
            prompt=prompt,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Expected: 22800 - 15000 - 100 = 7,700 tokens
        assert max_tokens == 7700

    def test_very_long_conversation_minimum_enforced(self):
        """
        Test that minimum response tokens are enforced.

        Scenario: Conversation history is so long that calculated
        max_response would be < 500 tokens
        Expected: Should enforce 500 token minimum
        """
        # 88,000 character prompt = 22,000 tokens
        prompt = "a" * 88000
        max_tokens = calculate_max_response_tokens(
            prompt=prompt,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Calculation: 22800 - 22000 - 100 = 700 tokens
        # But this is dangerously close, so minimum should apply
        # Actually 700 > 500, so it should return 700
        assert max_tokens == 700

    def test_extreme_conversation_minimum_enforced(self):
        """
        Test behavior when conversation is too long for minimum.

        Scenario: Conversation so long that even minimum_response would exceed safe zone
        Expected: Should return what's available (NOT minimum), logs ERROR
        """
        # 90,000 character prompt = 22,500 tokens
        prompt = "a" * 90000
        max_tokens = calculate_max_response_tokens(
            prompt=prompt,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Calculation: 22800 - 22500 - 100 = 200 tokens available
        # If we enforced minimum (500), total would be:
        # 22500 + 500 + 100 = 23100 tokens ❌ EXCEEDS SAFE_ZONE!
        # So we return what's available: 200 tokens
        # This triggers an ERROR log warning that history must be trimmed
        assert max_tokens == 200

    def test_critical_bug_scenario(self):
        """
        Test the CRITICAL BUG scenario that prompted this fix.

        BEFORE FIX:
        - Fixed max_tokens = 18,000
        - Conversation history = 5,000 tokens
        - TOTAL = 23,000 tokens ❌ EXCEEDS 22,800 → FAILURE

        AFTER FIX:
        - Dynamic max_tokens based on history
        - Conversation history = 5,000 tokens
        - max_response = 22,800 - 5,000 - 100 = 17,700
        - TOTAL = 22,700 tokens ✅ WITHIN SAFE_ZONE
        """
        # Simulate 5,000 token conversation history
        prompt = "a" * 20000  # 5,000 tokens

        max_tokens = calculate_max_response_tokens(
            prompt=prompt,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Verify we get dynamic max_tokens (17,700)
        assert max_tokens == 17700

        # Verify total stays within SAFE_ZONE_TOKEN
        prompt_tokens = estimate_tokens(prompt)
        total_tokens = prompt_tokens + max_tokens + 100  # +100 for safety buffer
        assert total_tokens <= 22800, f"Total {total_tokens} exceeds SAFE_ZONE_TOKEN 22800"


class TestSafeZoneEnforcement:
    """Integration tests verifying SAFE_ZONE_TOKEN is never exceeded."""

    @pytest.mark.parametrize("prompt_chars,expected_max_tokens", [
        (100, 22675),      # Tiny conversation
        (400, 22600),      # Small conversation (adjusted: 100 tokens, not 225)
        (4000, 21700),     # Medium conversation (1k tokens)
        (20000, 17700),    # Large conversation (5k tokens)
        (40000, 12700),    # Very large conversation (10k tokens)
        (60000, 7700),     # Extremely large conversation (15k tokens)
        (80000, 2700),     # Near-limit conversation (20k tokens)
        (88000, 700),      # At-limit conversation (22k tokens)
        (90000, 200),      # Over-limit (CANNOT use minimum, would exceed safe zone)
    ])
    def test_safe_zone_never_exceeded(self, prompt_chars, expected_max_tokens):
        """
        Parametrized test: Verify SAFE_ZONE_TOKEN is NEVER exceeded.

        Tests various conversation lengths from tiny to extreme.
        """
        prompt = "a" * prompt_chars
        max_tokens = calculate_max_response_tokens(
            prompt=prompt,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Verify expected calculation
        assert max_tokens == expected_max_tokens

        # CRITICAL: Verify total never exceeds SAFE_ZONE_TOKEN
        prompt_tokens = estimate_tokens(prompt)
        total_tokens = prompt_tokens + max_tokens + 100
        assert total_tokens <= 22800, (
            f"CRITICAL BUG: Total tokens {total_tokens} exceeds SAFE_ZONE_TOKEN 22800! "
            f"Prompt={prompt_tokens}, Response={max_tokens}, Buffer=100"
        )

    def test_real_world_conversation_example(self):
        """
        Test with realistic conversation data.

        Simulates actual GPT-OSS usage with IEC 62443 queries.
        """
        # Realistic conversation about IEC 62443
        messages = [
            {"role": "user", "content": "What is IEC 62443?"},
            {"role": "assistant", "content": "IEC 62443 is an international series of standards that address cybersecurity for operational technology in automation and control systems. It provides a flexible framework to address and mitigate current and future security vulnerabilities in industrial automation and control systems (IACS)."},
            {"role": "user", "content": "Tell me about CR 2.11"},
            {"role": "assistant", "content": "CR 2.11 (Component Requirement 2.11) is 'Unsuccessful login attempts' in IEC 62443-4-2. It requires that the control system component shall limit the number of unsuccessful authentication attempts that can occur in a configurable time period. When the limit is exceeded, the system shall either deny access for a configurable time period or notify the system administrator."},
            {"role": "user", "content": "How do I implement this for my SCADA system?"}
        ]

        # Build conversation prompt
        conversation_tokens = estimate_conversation_tokens(messages)

        # Convert to character count for prompt simulation
        # (Rough approximation for testing)
        prompt_chars = conversation_tokens * 4

        # Calculate max response tokens
        max_tokens = calculate_max_response_tokens(
            prompt="a" * prompt_chars,
            safe_zone_token=22800,
            safety_buffer=100,
            minimum_response=500
        )

        # Verify we have plenty of room for response
        assert max_tokens > 1000, "Should have enough tokens for detailed answer"

        # Verify total doesn't exceed safe zone
        total = conversation_tokens + max_tokens + 100
        assert total <= 22800


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
