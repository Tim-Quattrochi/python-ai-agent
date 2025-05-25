"""Configuration management for the AI Agent."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration class for the AI Agent."""

    # LLM Provider configuration
    llm_provider: str = "anthropic"  # "anthropic", "openai", or "local"

    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Model configuration
    anthropic_model: str = "claude-3-sonnet-20240229"
    openai_model: str = "gpt-4-turbo-preview"
    local_model: str = "/Users/timqmac/Library/Caches/llama.cpp/bartowski_Llama-3-Groq-8B-Tool-Use-GGUF_Llama-3-Groq-8B-Tool-Use-Q4_K_M.gguf"

    # Local LLM server configuration
    local_llm_url: str = "http://10.0.0.225:8080"

    # Agent behavior
    max_conversation_history: int = 50
    max_tool_calls_per_turn: int = 5

    def __post_init__(self):
        """Load configuration from environment variables."""
        self.llm_provider = os.getenv(
            "LLM_PROVIDER", self.llm_provider).lower()
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_model = os.getenv(
            "ANTHROPIC_MODEL", self.anthropic_model)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.local_model = os.getenv("LOCAL_MODEL", self.local_model)
        self.local_llm_url = os.getenv("LOCAL_LLM_URL", self.local_llm_url)

        # Validate configuration
        self._validate()

    def _validate(self):
        """Validate the configuration."""
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when using Anthropic provider")
        elif self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when using OpenAI provider")
        elif self.llm_provider == "local":
            # No API key validation needed for local
            pass
        elif self.llm_provider not in ["anthropic", "openai", "local"]:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    @property
    def current_api_key(self) -> str:
        """Get the API key for the current provider."""
        if self.llm_provider == "anthropic":
            return self.anthropic_api_key
        return self.openai_api_key

    @property
    def current_model(self) -> str:
        """Get the model for the current provider."""
        if self.llm_provider == "anthropic":
            return self.anthropic_model
        elif self.llm_provider == "openai":
            return self.openai_model
        else:
            return self.local_model


def get_config() -> Config:
    """Get the application configuration."""
    return Config()
