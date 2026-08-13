"""
Convert Kaggle electoral campaign datasets to JSON and upload to
gs://tfm-twitter-raw/candidate_tweets/

Datasets uploaded:
  trump_2016  → electoral_campaigns/trump_2016/tweets.csv         (Hamner, 2016)
  brexit_2016 → electoral_campaigns/brexit_kaggle.csv             (Chadjinik, 2020)
  trump_2024  → electoral_campaigns/trump24_kaggle.txt            (Kaggle, 2024)

Skipped:
  españa23_kaggle.csv → ends March 2023, elections were July 2023

JSON format mirrors twscrape output so loaders.py handles all sources uniformly.

Usage:
    cd TFM/
    python scripts/upload_electoral_campaigns.py
"""

import json
import os

import pandas as pd
from google.cloud import storage

# Use TFM service account — leaves system ADC (work projects) untouched
_SA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scrapper", "service-account.json"))
if os.path.exists(_SA) and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _SA

RAW_BUCKET = "tfm-twitter-raw"
CAMPAIGNS_DIR = os.path.join(os.path.dirname(__file__), "..", "electoral_campaigns")


# ── Converters ────────────────────────────────────────────────────────────────

def convert_trump2016(path: str) -> list[dict]:
    """tweets.csv: official @HillaryClinton + @realDonaldTrump tweets."""
    df = pd.read_csv(path, low_memory=False)
    df = df[df["lang"] == "en"].dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    tweets = []
    for _, row in df.iterrows():
        tweets.append({
            "id": int(row["id"]),
            "rawContent": row.get("text", ""),
            "date": str(row.get("time", "")),
            "lang": row.get("lang", "en"),
            "retweetCount": int(row["retweet_count"]) if pd.notna(row.get("retweet_count")) else 0,
            "likeCount": int(row["favorite_count"]) if pd.notna(row.get("favorite_count")) else 0,
            "isRetweet": bool(row.get("is_retweet", False)),
            "replyCount": 0,
            "user": {"username": row.get("handle", ""), "displayname": row.get("handle", "")},
            "_source": "kaggle_hamner2016",
            "_campaign": "trump_2016",
            "_data_type": "candidate_tweet",
            "original_author": row.get("original_author", None),
        })
    print(f"  trump_2016: {len(tweets):,} tweets | handles: {df['handle'].value_counts().to_dict()}")
    return tweets


def convert_brexit2016(path: str) -> list[dict]:
    """brexit_kaggle.csv: UK MP tweets with Stay/Leave stance labels."""
    df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
    df = df.dropna(subset=["id", "text"])
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    label_map = {"Stay": "remain", "Leave": "leave"}

    tweets = []
    for _, row in df.iterrows():
        tweets.append({
            "id": int(row["id"]),
            "rawContent": row.get("text", ""),
            "date": str(row.get("created_at", "")),
            "lang": "en",
            "retweetCount": 0,
            "likeCount": 0,
            "isRetweet": False,
            "replyCount": 0,
            "user": {
                "username": row.get("screen_name", ""),
                "displayname": row.get("name", ""),
            },
            "_source": "kaggle_chadjinik",
            "_campaign": "brexit_2016",
            "_data_type": "candidate_tweet",
            "_stance_label": label_map.get(str(row.get("label", "")), None),
        })
    label_dist = df["label"].value_counts().to_dict()
    print(f"  brexit_2016: {len(tweets):,} tweets | stance labels: {label_dist}")
    return tweets


def convert_trump2024(path: str) -> list[dict]:
    """trump24_kaggle.txt: public tweets Jun–Nov 2024 about the election."""
    df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
    df = df.dropna(subset=["Tweet ID", "Text"])
    df["Tweet ID"] = pd.to_numeric(df["Tweet ID"], errors="coerce")
    df = df.dropna(subset=["Tweet ID"])
    df["Tweet ID"] = df["Tweet ID"].astype(int)

    tweets = []
    for _, row in df.iterrows():
        tweets.append({
            "id": int(row["Tweet ID"]),
            "rawContent": row.get("Text", ""),
            "date": str(row.get("Date", "")),
            "lang": "en",
            "retweetCount": int(row["Retweets"]) if pd.notna(row.get("Retweets")) else 0,
            "likeCount": int(row["Likes"]) if pd.notna(row.get("Likes")) else 0,
            "isRetweet": False,
            "replyCount": 0,
            "user": {"username": str(row.get("Username", "")), "displayname": str(row.get("Username", ""))},
            "_source": "kaggle_trump2024",
            "_campaign": "trump_2024",
            "_data_type": "public_tweet",
            # Weight col is dataset-internal relevance score — not sentiment label, ignored
        })
    print(f"  trump_2024: {len(tweets):,} tweets | date range: {df['Date'].iloc[-1]} → {df['Date'].iloc[0]}")
    return tweets


# ── Upload ────────────────────────────────────────────────────────────────────

def upload(tweets: list[dict], gcs_path: str, client: storage.Client) -> None:
    payload = json.dumps(tweets, indent=2, ensure_ascii=False)
    blob = client.bucket(RAW_BUCKET).blob(gcs_path)
    blob.upload_from_string(payload, content_type="application/json")
    print(f"  → gs://{RAW_BUCKET}/{gcs_path}")


def main():
    client = storage.Client()

    datasets = [
        (
            "trump_2016",
            os.path.join(CAMPAIGNS_DIR, "trump_2016", "tweets.csv"),
            convert_trump2016,
            "candidate_tweets/trump_2016.json",
        ),
        (
            "brexit_2016",
            os.path.join(CAMPAIGNS_DIR, "brexit_kaggle.csv"),
            convert_brexit2016,
            "candidate_tweets/brexit_2016.json",
        ),
        (
            "trump_2024",
            os.path.join(CAMPAIGNS_DIR, "trump24_kaggle.txt"),
            convert_trump2024,
            "candidate_tweets/trump_2024.json",
        ),
    ]

    for name, path, converter, gcs_path in datasets:
        print(f"\nProcessing {name}...")
        if not os.path.exists(path):
            print(f"  SKIP — file not found: {path}")
            continue
        tweets = converter(path)
        upload(tweets, gcs_path, client)

    print("\nDone. Skipped: españa23_kaggle.csv (ends March 2023, elections July 2023).")


if __name__ == "__main__":
    main()
