"""Runtime configuration for the backend pipeline (B1 + B2).

Values come from environment variables (loaded from ``.env`` via python-dotenv).
See ``env.example`` for the full list. No secrets are hardcoded here.
"""

from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Pipeline settings resolved from the environment.

    The LLM is reached through an **OpenAI-compatible** client. ``LLM_PROVIDER``
    selects which set of variables is used; generic ``LLM_BASE_URL`` /
    ``LLM_API_KEY`` / ``LLM_MODEL`` always override the provider-specific ones.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # --- LLM provider selection -------------------------------------------
    llm_provider: str = Field(default="azure_foundry", alias="LLM_PROVIDER")

    # Generic OpenAI-compatible overrides (highest priority)
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")

    # Azure AI Foundry (Gemini / Grok / Llama … behind an OpenAI-compatible route)
    azure_foundry_endpoint: str | None = Field(default=None, alias="AZURE_FOUNDRY_ENDPOINT")
    azure_foundry_api_key: str | None = Field(default=None, alias="AZURE_FOUNDRY_API_KEY")
    azure_foundry_deployment_extractor: str = Field(
        default="gemini-1.5-pro", alias="AZURE_FOUNDRY_DEPLOYMENT_EXTRACTOR"
    )

    # Azure OpenAI
    azure_openai_endpoint: str | None = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str | None = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(
        default="2024-08-01-preview", alias="AZURE_OPENAI_API_VERSION"
    )
    azure_openai_deployment_extractor: str = Field(
        default="gpt-4o", alias="AZURE_OPENAI_DEPLOYMENT_EXTRACTOR"
    )

    # --- Shared LLM call parameters ---------------------------------------
    llm_temperature: float = Field(default=0.0, alias="LLM_TEMPERATURE")
    llm_max_output_tokens: int = Field(default=8192, alias="LLM_MAX_OUTPUT_TOKENS")
    llm_timeout_seconds: int = Field(default=120, alias="LLM_TIMEOUT_SECONDS")
    llm_max_retries: int = Field(default=2, alias="LLM_MAX_RETRIES")

    # --- Tika (B1) --------------------------------------------------------
    tika_server_url: str = Field(default="http://localhost:9998", alias="TIKA_SERVER_URL")
    tika_timeout_seconds: int = Field(default=60, alias="TIKA_TIMEOUT_SECONDS")

    # --- Deduplication / merge (B2) ---------------------------------------
    embedding_model_local: str = Field(
        default="intfloat/multilingual-e5-small", alias="EMBEDDING_MODEL_LOCAL"
    )
    merge_similarity_threshold: float = Field(
        default=0.93, alias="MERGE_SIMILARITY_THRESHOLD"
    )

    # --- Gap analysis / Company KB (B4) -----------------------------------
    # Backend della knowledge base aziendale:
    #   "local"    → legge i JSON del profilo + Qdrant in-memory (zero infra, per demo)
    #   "postgres" → PostgreSQL (system of record) + Qdrant server (indice derivato)
    kb_backend: str = Field(default="local", alias="KB_BACKEND")
    company_kb_dir: str = Field(
        default="docs/gap_analysys/DB_Completo/profilo_aziendale",
        alias="COMPANY_KB_DIR",
    )
    gap_embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        alias="GAP_EMBEDDING_MODEL",
    )
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection_competenze: str = Field(
        default="portfolio_competenze", alias="QDRANT_COLLECTION_COMPETENZE"
    )
    qdrant_collection_referenze: str = Field(
        default="portfolio_referenze", alias="QDRANT_COLLECTION_REFERENZE"
    )
    pg_dsn: str = Field(
        default="postgresql://sta:sta@localhost:5432/smart_tender", alias="PG_DSN"
    )

    @property
    def is_azure_openai(self) -> bool:
        return self.llm_base_url is None and self.llm_provider.lower() == "azure_openai"

    def resolve_llm(self) -> tuple[str, str, str]:
        """Return ``(base_url, api_key, model)`` for an OpenAI-compatible client.

        Raises:
            RuntimeError: if no usable endpoint/key/model can be resolved.
        """
        if self.llm_base_url and self.llm_api_key and self.llm_model:
            return self.llm_base_url, self.llm_api_key, self.llm_model

        provider = self.llm_provider.lower()
        if provider == "azure_foundry":
            base, key, model = (
                self.azure_foundry_endpoint,
                self.azure_foundry_api_key,
                self.azure_foundry_deployment_extractor,
            )
        elif provider == "azure_openai":
            base, key, model = (
                self.azure_openai_endpoint,
                self.azure_openai_api_key,
                self.azure_openai_deployment_extractor,
            )
        else:
            raise RuntimeError(
                f"Unknown LLM_PROVIDER={self.llm_provider!r}. "
                "Use 'azure_foundry', 'azure_openai', or set LLM_BASE_URL/LLM_API_KEY/LLM_MODEL."
            )

        if not base or not key:
            raise RuntimeError(
                f"Missing LLM endpoint or API key for provider {self.llm_provider!r}. "
                "Populate the matching variables in .env (see env.example)."
            )
        return base, key, model

    @model_validator(mode="after")
    def _normalise(self) -> Settings:
        # Strip accidental trailing whitespace from secrets pasted into .env
        if self.llm_api_key:
            object.__setattr__(self, "llm_api_key", self.llm_api_key.strip())
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached singleton so we read the environment only once per process."""
    return Settings()
