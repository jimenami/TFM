"""
Twitter scraper using twscrape.

Flow:
  1. Init twscrape API + load accounts from env
  2. For each query, fetch tweets within the campaign date range
  3. Serialize tweets as a JSON array
  4. Upload to GCS at: {prefix}/{campaign}/{task}/{target_or_sentiment}/{date}.json
"""
import asyncio
import json
import logging
import os
import random
from datetime import datetime, timezone
from pathlib import Path

from twscrape import API, gather
from twscrape.models import Tweet

from config import settings
from political_queries import get_all_queries

logger = logging.getLogger(__name__)


# ── GCS upload ───────────────────────────────────────────────────────────────

def _upload_to_gcs(content: str, gcs_path: str) -> None:
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(settings.gcs_bucket)
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(content.encode("utf-8"), content_type="application/json")
    logger.info(f"Uploaded {blob.public_url}")


def _gcs_path(campaign: str, task: str, target: str | None, run_date: str) -> str:
    subtask = target if target else "sentiment"
    parts = [p for p in [settings.gcs_prefix, campaign, task, subtask] if p]
    return "/".join(parts) + f"/{run_date}.json"


# ── Tweet serialization ───────────────────────────────────────────────────────

def _tweet_to_dict(tweet: Tweet, query_meta: dict) -> dict:
    return {
        "id": str(tweet.id),
        "text": tweet.rawContent,
        "created_at": tweet.date.isoformat() if tweet.date else None,
        "author_id": str(tweet.user.id) if tweet.user else None,
        "author_username": tweet.user.username if tweet.user else None,
        "lang": tweet.lang,
        "like_count": tweet.likeCount,
        "retweet_count": tweet.retweetCount,
        "reply_count": tweet.replyCount,
        "quote_count": tweet.quoteCount,
        "is_retweet": tweet.retweetedTweet is not None,
        "hashtags": [h.lower() for h in (tweet.hashtags or [])],
        "campaign": query_meta["campaign"],
        "task": query_meta["task"],
        "target": query_meta["target"],
        "query_slug": query_meta["slug"],
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Account pool setup ────────────────────────────────────────────────────────

async def _setup_accounts(api: API) -> None:
    """
    Parse TWITTER_ACCOUNTS env var and add to pool.

    Formats (comma-separated for multiple accounts):
      user:pass:email:email_pass                          — login flow (may hit Cloudflare)
      user:pass:email:email_pass:ct0_value:auth_token     — cookie-based (bypasses Cloudflare)
    """
    raw = settings.twitter_accounts.strip()
    if not raw:
        raise ValueError("TWITTER_ACCOUNTS env var is empty — add at least one account")

    accounts = [a.strip() for a in raw.split(",") if a.strip()]
    needs_login = []

    for entry in accounts:
        parts = entry.split(":")
        if len(parts) == 6:
            # Cookie-based — already authenticated, skip login flow
            username, password, email, email_password, ct0, auth_token = parts
            cookies = f"ct0={ct0}; auth_token={auth_token}"
            await api.pool.add_account(username, password, email, email_password, cookies=cookies)
            logger.info(f"Account added (cookies): @{username}")
        elif len(parts) == 4:
            username, password, email, email_password = parts
            await api.pool.add_account(username, password, email, email_password)
            needs_login.append(username)
            logger.info(f"Account added (login): @{username}")
        else:
            logger.warning(f"Skipping malformed entry: {entry!r}")

    if needs_login:
        logger.info(f"Logging in accounts: {needs_login}")
        await api.pool.login_all()
    else:
        logger.info("All accounts use cookies — skipping login_all()")


# ── Core scraping ─────────────────────────────────────────────────────────────

async def scrape_query(api: API, query_meta: dict, run_date: str) -> int:
    """
    Scrape one query and upload results to GCS.
    Returns number of tweets collected.
    """
    query = query_meta["query"]
    campaign = query_meta["campaign"]
    task = query_meta["task"]
    target = query_meta["target"]
    slug = query_meta["slug"]

    logger.info(f"[{slug}] Scraping: {query!r}")

    tweets_collected = []
    seen_ids: set[str] = set()

    try:
        async for tweet in api.search(query, limit=settings.max_tweets_per_query):
            tid = str(tweet.id)
            if tid in seen_ids:
                continue
            seen_ids.add(tid)

            if not settings.include_retweets and tweet.retweetedTweet is not None:
                continue

            if tweet.likeCount < settings.min_likes:
                continue

            tweets_collected.append(_tweet_to_dict(tweet, query_meta))

    except Exception as e:
        logger.error(f"[{slug}] Scraping failed: {e}")
        return 0

    if not tweets_collected:
        logger.warning(f"[{slug}] No tweets collected")
        return 0

    # Serialize to JSON array
    content = json.dumps(tweets_collected, ensure_ascii=False, indent=2)

    gcs_path = _gcs_path(campaign, task, target, run_date)
    # Append slug to avoid overwriting when multiple queries share the same path
    gcs_path = gcs_path.replace(".json", f"_{slug}.json")

    try:
        _upload_to_gcs(content, gcs_path)
    except Exception as e:
        logger.error(f"[{slug}] GCS upload failed: {e}")
        # Fallback: save locally
        local_path = Path(f"/tmp/{slug}_{run_date}.json")
        local_path.write_text(content, encoding="utf-8")
        logger.info(f"[{slug}] Saved locally to {local_path}")

    return len(tweets_collected)


async def run_scraper(
    campaigns: list[str] | None = None,
    task: str = "all",
    targets: list[str] | None = None,
) -> dict[str, int]:
    """
    Main entry point. Scrapes all requested campaigns and tasks.

    Args:
        campaigns: campaign slugs to run (None = all)
        task: "sentiment" | "stance" | "all"
        targets: stance target slugs to filter (None = all)

    Returns:
        Dict mapping query slug → tweet count
    """
    if settings.google_application_credentials:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials

    run_date = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    queries = get_all_queries(campaigns=campaigns, task=task, targets=targets)

    logger.info(f"Starting scraper — {len(queries)} queries, run_date={run_date}")

    # twscrape stores account pool in a local SQLite DB
    api = API()
    await _setup_accounts(api)

    results: dict[str, int] = {}
    for query_meta in queries:
        count = await scrape_query(api, query_meta, run_date)
        results[query_meta["slug"]] = count
        # Random delay — human-like behavior
        delay = random.uniform(settings.min_delay, settings.max_delay)
        logger.info(f"Sleeping {delay:.1f}s before next query...")
        await asyncio.sleep(delay)

    total = sum(results.values())
    logger.info(f"Done. Total tweets collected: {total}")
    for slug, count in results.items():
        logger.info(f"  {slug}: {count}")

    return results
