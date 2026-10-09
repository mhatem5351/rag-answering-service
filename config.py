from pydantic import AliasChoices, Field, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Standard OPENAI_API_KEY first; the older OpenAI_KEY_TOKEN name is still accepted.
    openai_api_key: str = Field(
        validation_alias=AliasChoices("OPENAI_API_KEY", "OpenAI_KEY_TOKEN"),
    )
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    default_top_k: int = 3
    max_query_length: int = 500
    denied_terms: list[str] = [
        "ignore previous instructions",
        "system prompt",
        "jailbreak",
        "bypass",
        "hack the",
        "drop table",
        "DELETE FROM",
        "<script>",
    ]
    hit_rate_threshold: float = 0.35

    model_config = {"env_file": ".env", "env_ignore_empty": True}


def _load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        if any(err["type"] == "missing" for err in exc.errors()):
            raise RuntimeError(
                "OpenAI API key not found. Set OPENAI_API_KEY (or the older "
                "OpenAI_KEY_TOKEN) in the environment or in a .env file."
            ) from exc
        raise


settings = _load_settings()
