"""
Data loaders for TFM pipeline.

Handles:
  - TweetEval splits from HuggingFace datasets
  - Scraped tweets from GCS bucket (JSON)
  - Candidate tweets CSV (trump_2016 official accounts)
  - Stratified re-split of TweetEval train+val
"""

import json
import os
from pathlib import Path
from typing import Optional

# Use TFM service account — leaves system ADC (work projects) untouched
_SA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scrapper", "service-account.json"))
if os.path.exists(_SA) and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _SA

import pandas as pd
from sklearn.model_selection import train_test_split

# ── TweetEval ─────────────────────────────────────────────────────────────────

TWEETEVAL_SENTIMENT_TASKS = ["sentiment"]
TWEETEVAL_STANCE_TASKS = [
    "stance_abortion",
    "stance_atheism",
    "stance_climate",
    "stance_feminist",
    "stance_hillary",
]

LABEL_MAP_SENTIMENT = {0: "negative", 1: "neutral", 2: "positive"}
LABEL_MAP_STANCE = {0: "against", 1: "favor", 2: "neither"}


def load_tweeteval(task: str) -> dict:
    """
    Load TweetEval task from HuggingFace.
    Returns dict with keys 'train', 'validation', 'test' as DataFrames.

    Args:
        task: one of 'sentiment', 'stance_abortion', etc.
    """
    from datasets import load_dataset  # lazy import — not needed for loaders only

    ds = load_dataset("cardiffnlp/tweet_eval", task)
    result = {}
    for split_name in ["train", "validation", "test"]:
        df = ds[split_name].to_pandas()
        df = df.rename(columns={"label": "label_id"})
        if "sentiment" in task:
            df["label"] = df["label_id"].map(LABEL_MAP_SENTIMENT)
        else:
            df["label"] = df["label_id"].map(LABEL_MAP_STANCE)
        result[split_name] = df
    return result


def stratified_resplit(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    val_size: float = 0.1,
    label_col: str = "label_id",
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Combine train+val and re-split stratified.
    Fixes the high-variance issue from TweetEval's small val sets (stance: 40-70 samples).

    Returns (new_train_df, new_val_df).
    """
    combined = pd.concat([train_df, val_df], ignore_index=True)
    new_train, new_val = train_test_split(
        combined,
        test_size=val_size,
        stratify=combined[label_col],
        random_state=random_state,
    )
    return new_train.reset_index(drop=True), new_val.reset_index(drop=True)


# ── Scraped data (GCS) ────────────────────────────────────────────────────────

def load_scraped_from_local(data_dir: str, campaign: Optional[str] = None) -> pd.DataFrame:
    """
    Load scraped tweet JSONs from a local directory (downloaded from GCS).
    Each JSON file contains a list of tweet dicts.

    Args:
        data_dir: path to directory with *.json files (one per query).
        campaign: if provided, filter files by campaign prefix.

    Returns:
        DataFrame with columns from tweet dicts + 'campaign' column.
    """
    data_path = Path(data_dir)
    pattern = f"{campaign}_*.json" if campaign else "*.json"
    files = sorted(data_path.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No JSON files found in {data_dir} (pattern: {pattern})")

    records = []
    for f in files:
        with open(f) as fh:
            tweets = json.load(fh)
        for t in tweets:
            t["_source_file"] = f.name
            # infer campaign from filename prefix
            if "_" in f.stem:
                t["campaign"] = f.stem.split("_")[0]
            records.append(t)

    df = pd.json_normalize(records)
    return df


def load_scraped_from_gcs(bucket: str, prefix: str = "", campaign: Optional[str] = None) -> pd.DataFrame:
    """
    Load scraped tweet JSONs directly from GCS.
    Requires google-cloud-storage installed and ADC credentials set.

    Args:
        bucket: GCS bucket name (e.g. 'tfm-twitter-raw').
        prefix: object prefix to filter (e.g. 'trump_2024/').
        campaign: if set, filter blobs by campaign name in their path.
    """
    from google.cloud import storage  # lazy import

    client = storage.Client()
    blobs = list(client.list_blobs(bucket, prefix=prefix))

    if campaign:
        blobs = [b for b in blobs if campaign in b.name]

    records = []
    for blob in blobs:
        data = json.loads(blob.download_as_text())
        if isinstance(data, list):
            for t in data:
                t["_blob"] = blob.name
                records.append(t)

    if not records:
        raise ValueError(f"No tweets loaded from gs://{bucket}/{prefix}")

    return pd.json_normalize(records)


def deduplicate_tweets(df: pd.DataFrame, id_col: str = "id") -> pd.DataFrame:
    """
    Remove duplicate tweets by ID.
    Critical for españa_2023 (re-ran after DNS failure — overlapping queries).
    """
    before = len(df)
    df = df.drop_duplicates(subset=[id_col])
    after = len(df)
    if before != after:
        print(f"Deduplicated: {before} → {after} tweets (removed {before - after})")
    return df.reset_index(drop=True)


# ── Candidate tweets CSV (electoral_campaigns) ────────────────────────────────

def load_candidate_tweets_csv(csv_path: str) -> pd.DataFrame:
    """
    Load trump_2016 candidate tweets CSV from electoral_campaigns/.
    Has columns: id, handle, text, is_retweet, time, lang, retweet_count, favorite_count, ...

    Returns cleaned DataFrame with parsed datetime.
    """
    df = pd.read_csv(csv_path, low_memory=False)
    # keep only useful columns
    keep = ["id", "handle", "text", "is_retweet", "time", "lang", "retweet_count", "favorite_count"]
    available = [c for c in keep if c in df.columns]
    df = df[available].copy()
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    # only English tweets
    if "lang" in df.columns:
        df = df[df["lang"] == "en"]
    return df.reset_index(drop=True)
