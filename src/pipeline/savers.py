"""
Save processed DataFrames to GCS as Parquet.

Bucket: tfm-twitter-processed  (must exist — create once via gcloud or console)
Format: Parquet (typed, compressed, fast to reload in notebooks)
"""

import io
import os
from typing import Optional

import pandas as pd

# Use TFM service account — leaves system ADC (work projects) untouched
_SA = os.path.join(os.path.dirname(__file__), "..", "..", "scrapper", "service-account.json")
_SA = os.path.abspath(_SA)
if os.path.exists(_SA) and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _SA

PROCESSED_BUCKET = "tfm-twitter-processed"


def _gcs_client():
    from google.cloud import storage
    return storage.Client()


def save_df_to_gcs(
    df: pd.DataFrame,
    gcs_path: str,
    bucket: str = PROCESSED_BUCKET,
    verbose: bool = True,
) -> str:
    """
    Save DataFrame as Parquet to GCS.

    Args:
        df: DataFrame to save.
        gcs_path: object path inside bucket (e.g. 'tweeteval/sentiment/train.parquet').
        bucket: GCS bucket name.
        verbose: print confirmation.

    Returns:
        Full GCS URI (gs://bucket/path).
    """
    # Sanitize mixed-type object columns so pyarrow can serialize them
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str)

    client = _gcs_client()
    buf = io.BytesIO()
    df.to_parquet(buf, index=False, engine="pyarrow")
    buf.seek(0)

    blob = client.bucket(bucket).blob(gcs_path)
    blob.upload_from_file(buf, content_type="application/octet-stream")

    uri = f"gs://{bucket}/{gcs_path}"
    if verbose:
        print(f"Saved {len(df):,} rows → {uri}")
    return uri


def save_tweeteval_splits(
    splits: dict,
    task: str,
    bucket: str = PROCESSED_BUCKET,
) -> dict:
    """
    Save train/val/test splits for a TweetEval task.

    Args:
        splits: dict with keys 'train', 'validation', 'test' as DataFrames.
        task: e.g. 'sentiment', 'stance_abortion'.

    Returns:
        Dict of {split_name: gcs_uri}.
    """
    uris = {}
    for split_name, df in splits.items():
        path = f"tweeteval/{task}/{split_name}.parquet"
        uris[split_name] = save_df_to_gcs(df, path, bucket=bucket)
    return uris


def save_scraped_campaign(
    df: pd.DataFrame,
    campaign: str,
    bucket: str = PROCESSED_BUCKET,
) -> str:
    """Save processed scraped tweets for one campaign."""
    path = f"scraped/{campaign}.parquet"
    return save_df_to_gcs(df, path, bucket=bucket)


def save_candidate_tweets(
    df: pd.DataFrame,
    campaign: str,
    bucket: str = PROCESSED_BUCKET,
) -> str:
    """Save candidate (official account) tweets."""
    path = f"candidate_tweets/{campaign}.parquet"
    return save_df_to_gcs(df, path, bucket=bucket)


# ── Loaders for processed data ─────────────────────────────────────────────────

def load_processed(
    gcs_path: str,
    bucket: str = PROCESSED_BUCKET,
) -> pd.DataFrame:
    """
    Load any processed Parquet file from GCS.
    Use in modeling notebooks after 01_preprocessing.ipynb ran.
    """
    client = _gcs_client()
    blob = client.bucket(bucket).blob(gcs_path)
    buf = io.BytesIO(blob.download_as_bytes())
    return pd.read_parquet(buf)


def load_tweeteval_processed(task: str, split: str, bucket: str = PROCESSED_BUCKET) -> pd.DataFrame:
    """Shortcut: load one processed TweetEval split."""
    return load_processed(f"tweeteval/{task}/{split}.parquet", bucket=bucket)


def load_scraped_processed(campaign: str, bucket: str = PROCESSED_BUCKET) -> pd.DataFrame:
    """Shortcut: load processed scraped data for one campaign."""
    return load_processed(f"scraped/{campaign}.parquet", bucket=bucket)
