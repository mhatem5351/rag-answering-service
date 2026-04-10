from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
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

    model_config = {"env_file": ".env"}


settings = Settings()
