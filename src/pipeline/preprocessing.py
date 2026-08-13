"""
Tweet preprocessing for TFM sentiment/stance analysis.

Variant A (BERTweet-style): normalize @mentions → @USER, URLs → HTTPURL.
  Keep hashtags, emojis, punctuation. Used for transformer fine-tuning.

Variant B (LDA-clean): lowercase, strip URLs/mentions/punctuation/stopwords.
  Used for topic modeling only.

Reference: Nguyen et al. (2020) BERTweet — same normalization as pretraining.
"""

import re
import unicodedata
from typing import Optional

import pandas as pd

# ── Patterns ──────────────────────────────────────────────────────────────────

_URL_RE = re.compile(
    r"https?://\S+|www\.\S+|t\.co/\S+",
    re.IGNORECASE,
)
_MENTION_RE = re.compile(r"@\w+")
_SEMST_RE = re.compile(r"#semst\b", re.IGNORECASE)
_AMPERSAND_RE = re.compile(r"&amp;")
_MULTI_SPACE_RE = re.compile(r"\s+")

# Minimal stopwords for LDA variant (Spanish + English basics)
_STOPWORDS_EN = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "it", "this", "that", "i",
    "he", "she", "we", "you", "they", "be", "have", "do", "not", "no",
    "by", "from", "as", "up", "out", "if", "than", "so", "its", "my",
    "our", "their", "will", "can", "just", "about", "over", "after",
    "also", "been", "has", "had", "me", "him", "her", "us", "them",
    "which", "who", "what", "when", "where", "how", "all", "more",
    "your", "there", "would", "could", "should",
}
_STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
    "al", "en", "y", "o", "pero", "si", "no", "es", "son", "era",
    "que", "con", "por", "para", "como", "más", "muy", "ya", "yo",
    "él", "ella", "nosotros", "vosotros", "ellos", "su", "sus", "mi",
    "tu", "se", "le", "les", "me", "nos", "también", "este", "esta",
    "esto", "ese", "esa", "eso", "hay", "ser", "estar", "todo", "esta",
}
_STOPWORDS = _STOPWORDS_EN | _STOPWORDS_ES


# ── Core normalization functions ───────────────────────────────────────────────

def decode_html_entities(text: str) -> str:
    """Replace &amp; and common HTML entities."""
    text = _AMPERSAND_RE.sub("&", text)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return text


def normalize_tweet_bertweet(text: str) -> str:
    """
    Variant A: BERTweet-style normalization.
    - @mention → @USER
    - http/https/t.co URL → HTTPURL
    - &amp; → &
    - collapse whitespace
    - keep hashtags, emojis, punctuation, case
    """
    text = decode_html_entities(text)
    text = _MENTION_RE.sub("@USER", text)
    text = _URL_RE.sub("HTTPURL", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip()
    return text


def remove_semst(text: str) -> str:
    """Remove #semst artifact from TweetEval stance data (SemEval-2016 collection tag)."""
    text = _SEMST_RE.sub("", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip()
    return text


def normalize_tweet_lda(text: str, lang: str = "en") -> str:
    """
    Variant B: aggressive cleaning for LDA topic modeling.
    - lowercase
    - remove URLs, @mentions, #hashtag symbols (keep word), punctuation, numbers
    - remove stopwords (EN + ES combined — safe for mixed corpora)
    - collapse whitespace
    """
    text = decode_html_entities(text)
    text = _URL_RE.sub(" ", text)
    text = _MENTION_RE.sub(" ", text)
    text = re.sub(r"#(\w+)", r"\1", text)     # strip # but keep word
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)      # remove punctuation
    text = re.sub(r"\d+", " ", text)          # remove numbers
    tokens = text.split()
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 2]
    return " ".join(tokens)


# ── TweetEval-specific preprocessing ─────────────────────────────────────────

def preprocess_tweeteval_sentiment(text: str) -> str:
    """BERTweet normalization for TweetEval sentiment split."""
    return normalize_tweet_bertweet(text)


def preprocess_tweeteval_stance(text: str) -> str:
    """BERTweet normalization + remove #semst for TweetEval stance split."""
    text = remove_semst(text)
    return normalize_tweet_bertweet(text)


# ── Batch DataFrame processing ────────────────────────────────────────────────

def preprocess_df(
    df: pd.DataFrame,
    text_col: str = "text",
    variant: str = "bertweet",
    is_stance: bool = False,
    output_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    Apply preprocessing to a DataFrame column in-place.

    Args:
        df: input DataFrame.
        text_col: column with raw tweet text.
        variant: 'bertweet' (Variant A) or 'lda' (Variant B).
        is_stance: if True, also strips #semst (only for TweetEval stance).
        output_col: write result to this column (default: overwrite text_col).

    Returns:
        DataFrame with processed text (copy).
    """
    df = df.copy()
    out = output_col or text_col

    if variant == "bertweet":
        fn = preprocess_tweeteval_stance if is_stance else preprocess_tweeteval_sentiment
    elif variant == "lda":
        fn = normalize_tweet_lda
    else:
        raise ValueError(f"Unknown variant '{variant}'. Choose 'bertweet' or 'lda'.")

    df[out] = df[text_col].fillna("").astype(str).map(fn)
    return df


# ── Scraped data (GCS JSON) ───────────────────────────────────────────────────

def preprocess_scraped_tweet(tweet: dict) -> dict:
    """
    Normalize a single tweet dict from GCS JSON output.
    Adds 'text_clean' key (Variant A). Original 'rawContent' unchanged.
    """
    raw = tweet.get("rawContent") or tweet.get("text") or ""
    tweet = dict(tweet)
    tweet["text_clean"] = normalize_tweet_bertweet(raw)
    return tweet


def preprocess_scraped_batch(tweets: list[dict]) -> list[dict]:
    """Apply preprocess_scraped_tweet to a list of tweet dicts."""
    return [preprocess_scraped_tweet(t) for t in tweets]
