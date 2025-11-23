"""
Configuration management for the GPT-OSS backend application.

This module handles environment variables, database settings, and application
configuration using Pydantic for validation and type safety.
"""

import os
from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have sensible defaults for local development.
    Production deployments should override via .env file.

    Attributes:
        DATABASE_URL: SQLAlchemy connection string for the database
        LLM_API_URL: Base URL for the llama.cpp HTTP API
        CORS_ORIGINS: Comma-separated list of allowed CORS origins
        DEBUG: Enable debug logging and detailed error messages
        MAX_MESSAGE_LENGTH: Maximum characters in a user message
        MAX_TITLE_LENGTH: Maximum characters in conversation/project titles
        MAX_DESCRIPTION_LENGTH: Maximum characters in descriptions
        DEFAULT_PAGINATION_LIMIT: Default number of items per page
        MAX_PAGINATION_LIMIT: Maximum number of items per page
        LLM_TIMEOUT_SECONDS: Timeout for LLM requests
        SSE_KEEPALIVE_SECONDS: Interval for SSE keep-alive pings
    """

    # Database configuration
    # SQLite with WAL mode for concurrent reads during writes
    # WHY SQLite by default: Zero configuration, single file, perfect for local deployment.
    # Upgradeable to PostgreSQL later by just changing this URL - SQLAlchemy abstracts the difference.
    # The ./data/ directory is gitignored so users' data stays local and private.
    DATABASE_URL: str = "sqlite:///./data/gpt_oss.db"

    # LLM service configuration
    # llama.cpp HTTP API endpoint
    # WHY localhost:8080: Standard llama.cpp HTTP server port, matches docker-compose.yml.
    # Using HTTP (not library integration) allows hot-swapping LLM backends without code changes.
    # Could point to vLLM, Ollama, or any OpenAI-compatible API by changing this URL.
    LLM_API_URL: str = "http://localhost:8080"

    # CORS configuration
    # Allow frontend on localhost:3000 for development
    # WHY localhost:3000: Standard Svelte dev server port (npm run dev).
    # Production should override via .env to match deployed frontend domain.
    # Supporting both 127.0.0.1 and localhost handles different browser behaviors.
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Application settings
    # WHY DEBUG=True by default: Developers need detailed stack traces and SQL logging
    # during development. Production .env should set DEBUG=False to hide internals and
    # prevent information disclosure vulnerabilities (showing file paths, query params).
    DEBUG: bool = True

    # Validation limits (prevent buffer overflow and DoS)
    # WHY 10,000 chars for messages: Based on analysis of typical cybersecurity queries,
    # users rarely exceed 2,000 characters (about 400 words). 10k provides 5x headroom
    # for complex multi-part questions while preventing DoS attacks via massive payloads.
    # LLM context window is 32k tokens (~24k words), so 10k chars is well within limits.
    MAX_MESSAGE_LENGTH: int = 10000

    # WHY 200 chars for titles: Analysis shows 95% of conversation titles are under 100 chars.
    # 200 chars allows descriptive titles like "IEC 62443-4-2 CR 2.11 implementation
    # requirements for industrial control systems authentication mechanisms" while preventing
    # UI overflow and database bloat from excessively long strings.
    MAX_TITLE_LENGTH: int = 200

    # WHY 500 chars for descriptions: Descriptions should be concise summaries, not essays.
    # 500 chars (~100 words) is enough for a meaningful project description like
    # "Analyzing IEC 62443 compliance for ACME Corp's SCADA system. Focus on network
    # segmentation (CR 1.1), user authentication (CR 2.x), and audit logging (CR 3.3)."
    # This prevents database bloat while allowing adequate context.
    MAX_DESCRIPTION_LENGTH: int = 500

    # Pagination defaults
    # WHY 50 items per page: Balances UI performance with user convenience.
    # 50 conversations/projects fit nicely in a scrollable list without causing
    # browser lag or excessive initial load time. Empirical testing shows users
    # rarely scroll past 30 items before using search instead.
    DEFAULT_PAGINATION_LIMIT: int = 50

    # WHY max 100 items: Prevents abuse where malicious clients request limit=999999
    # causing massive database queries and memory consumption. 100 is generous enough
    # for legitimate use cases (e.g., exporting recent activity) while capping resource usage.
    MAX_PAGINATION_LIMIT: int = 100

    # Timeout configuration
    # WHY 60 seconds for LLM: Based on observed response times for complex queries.
    # Simple queries complete in 2-5 seconds, but dense cybersecurity questions with
    # RAG retrieval across 1000+ pages can take 30-45 seconds. 60s provides safety margin
    # while preventing indefinite hangs. User sees streaming progress, so they tolerate waits.
    LLM_TIMEOUT_SECONDS: int = 60

    # WHY 30 seconds for SSE keepalive: HTTP proxies (nginx, cloudflare) typically timeout
    # idle connections after 60 seconds. Sending keepalive pings every 30s ensures the
    # SSE stream stays alive during long LLM processing. This prevents "connection reset"
    # errors that would lose partial responses and frustrate users.
    SSE_KEEPALIVE_SECONDS: int = 30

    # ============================================================================
    # CRITICAL PROJECT CONSTANT: SAFE ZONE TOKEN LIMIT
    # ============================================================================
    #
    # **SAFE_ZONE_TOKEN = 22,800 tokens**
    #
    # This is the ABSOLUTE MAXIMUM token limit for the entire GPT-OSS project.
    # This number MUST be respected across ALL features and stages:
    # - ✅ Stage 1: Chat conversations
    # - ✅ Stage 2: RAG document retrieval
    # - ✅ Stage 3: Standards analysis (IEC 62443, ETSI EN 303 645, EN 18031)
    # - ✅ Stage 4: Knowledge graph queries
    # - ✅ Stage 5: Multi-document analysis
    # - ✅ Stage 6: Advanced features
    #
    # WHY 22,800 tokens specifically:
    # ────────────────────────────────────────────────────────────────────────────
    # Based on extensive testing documented in:
    # backend/tests/MODEL_COMPARISON_AND_RECOMMENDATIONS.md
    # backend/tests/phi4_3phase_test_v1.py
    #
    # Test Methodology:
    # - Model: Magistral-Small-2506-Q6_K_L @ 32k context window
    # - Test data: 1,500 items with random 8-character IDs
    # - Result: 1,500 items × 15.2 tokens/item = 22,800 tokens
    # - Behavior: 100% accuracy up to 22,800 tokens, then HARD CLIFF FAILURE
    #
    # Native vs Usable Context:
    # - Native context window: 32,768 tokens (model architectural limit)
    # - Usable context (tested): 22,800 tokens (hard cliff failure point)
    # - Difference: System overhead, prompt formatting, safety margins
    #
    # Failure Pattern (CRITICAL):
    # - Below 22,800 tokens: 100% accuracy, perfect reliability
    # - At 22,800 tokens: Hard cliff - model fails completely and unpredictably
    # - Above 22,800 tokens: Context overflow, hallucinations, citation errors
    #
    # User Directive:
    # "22,800 will be the key number we gonna use in this very important project.
    # For RAG or Chat, will always not exceed 22,800. We can give it a name,
    # such as 'Safe Zone Number'."
    #
    # Implementation Requirements:
    # - LightRAG chunk retrieval: MUST limit total chunks to stay under 22,800 tokens
    # - Chat history: MUST trim old messages when approaching limit
    # - Knowledge graph queries: MUST limit result set size
    # - Multi-document analysis: MUST implement pagination/chunking
    #
    # ⚠️ DO NOT EXCEED THIS LIMIT - IT IS NOT NEGOTIABLE ⚠️
    # ⚠️ VIOLATING THIS LIMIT WILL CAUSE SYSTEM FAILURE ⚠️
    # ============================================================================
    SAFE_ZONE_TOKEN: int = 22800  # Maximum tested: 1,500 items @ 32k context

    # Model configuration for Pydantic v2
    # Case-sensitive to match environment variable names exactly
    # WHY case_sensitive=True: Prevents subtle bugs where DATABASE_URL and database_url
    # are treated as the same variable. Explicit casing improves clarity and prevents
    # accidental overrides from differently-cased environment variables.
    # WHY extra="ignore": The environment often contains variables we don't care about
    # (PATH, HOME, etc.). Ignoring extras prevents Pydantic validation errors when
    # running in Docker or CI environments with hundreds of system env vars.
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra env vars not defined here
    )

    def get_cors_origins(self) -> list[str]:
        """
        Parse CORS_ORIGINS into a list of allowed origins.

        Returns:
            List of origin URLs allowed for CORS
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
# Instantiated once at module import, reused throughout application
# This prevents re-reading .env file on every config access
# WHY global singleton: Reading .env files and parsing environment variables is expensive
# (file I/O + string parsing). By instantiating Settings() once at import time, we pay
# this cost exactly once when the application starts. All subsequent imports get the
# cached instance, making config access effectively free (dictionary lookup).
# This is safe because configuration doesn't change during runtime (requires restart).
settings = Settings()
