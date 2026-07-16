"""
Configuration via environment variables.
Set values in .env — no hardcoded credentials.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.absolute()
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    # Google Cloud Storage
    gcs_bucket: str
    gcs_prefix: str = "twitter/raw"
    google_application_credentials: str | None = None  # path to service account JSON

    # twscrape — pool of Twitter accounts (comma-separated "username:password:email:email_password")
    # At least one account required. More accounts = higher throughput.
    twitter_accounts: str

    # Scraping parameters
    max_tweets_per_query: int = 500
    lang: str = "es"
    min_likes: int = 0       # filter low-engagement noise if needed
    include_retweets: bool = False

    # Tasks to run: "sentiment", "stance", or "all"
    task: str = "all"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
