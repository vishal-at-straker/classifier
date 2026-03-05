"""
Application configuration from environment variables.
All configurable values come from env; no hardcoded secrets.
"""
import os
from functools import lru_cache


@lru_cache
def get_settings():
    """Load and return settings from environment."""
    return Settings()


class Settings:
    """Application settings from environment."""

    def __init__(self):
        self.database_url: str = os.getenv(
            "DATABASE_URL", "sqlite:///./classifier.db"
        )
        self.litellm_model: str = os.getenv("LITELLM_MODEL", "gpt-4o-mini")
        self.litellm_api_base: str = os.getenv("LITELLM_API_BASE", "")
        self.litellm_api_key: str = os.getenv("LITELLM_API_KEY", "")
        self.custom_llm_provider: str = os.getenv("CUSTOM_LLM_PROVIDER", "openai")
        self.litellm_temperature: float = float(os.getenv("LITELLM_TEMPERATURE", "0"))
        self.litellm_api_version: str = os.getenv("LITELLM_API_VERSION", "")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.environment: str = os.getenv("ENVIRONMENT", "dev")
        self.rate_limit_requests: int = int(
            os.getenv("RATE_LIMIT_REQUESTS", "60")
        )
        self.rate_limit_window_seconds: int = int(
            os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
        )
        self.submission_max_length: int = int(
            os.getenv("SUBMISSION_MAX_LENGTH", "10000")
        )
        # Optional team API base URLs
        self.team_engineering_url: str = os.getenv("TEAM_ENGINEERING_URL", "")
        self.team_customer_support_url: str = os.getenv(
            "TEAM_CUSTOMER_SUPPORT_URL", ""
        )
        self.team_product_management_url: str = os.getenv(
            "TEAM_PRODUCT_MANAGEMENT_URL", ""
        )
        self.team_feedback_url: str = os.getenv("TEAM_FEEDBACK_URL", "")
        self.team_escalation_url: str = os.getenv("TEAM_ESCALATION_URL", "")
        self.team_localization_url: str = os.getenv("TEAM_LOCALIZATION_URL", "")
        self.team_discard_url: str = os.getenv("TEAM_DISCARD_URL", "")
        # Prompts directory (default: prompts/ under project root)
        self.prompts_dir: str = os.getenv(
            "TRIAGE_PROMPTS_DIR",
            os.path.join(os.getcwd(), "prompts"),
        )
