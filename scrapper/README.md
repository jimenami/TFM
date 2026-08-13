# Twitter Political Campaign Scraper

Scrapes tweets from four electoral campaigns and uploads raw JSONL to Google Cloud Storage.

**Campaigns:**
| Slug | Campaign | Lang | Period |
|---|---|---|---|
| `brexit_2016` | Brexit Referendum | EN | Apr–Jun 2016 |
| `trump_2016` | US Election 2016 | EN | Sep–Nov 2016 |
| `españa_2023` | Elecciones Generales 23J | ES | Jun–Jul 2023 |
| `trump_2024` | US Election 2024 | EN | Sep–Nov 2024 |

**GCS output path:** `{GCS_BUCKET}/{GCS_PREFIX}/{campaign}/{task}/{target}/{run_date}.json`

---

## Prerequisites

- Docker + Docker Compose
- GCS bucket + service account JSON with `storage.objects.create` permission
- At least one Twitter/X account (free account works)

---

## Setup

```bash
cd scrapper
cp .env.example .env
```

Edit `.env`:

```env
GCS_BUCKET=my-tfm-bucket
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json

# One or more Twitter accounts: username:password:email:email_password
TWITTER_ACCOUNTS=myuser:mypass:myemail@gmail.com:emailpass
```

If using a service account JSON file, place it inside the `scrapper/` folder so Docker can access it.

---

## Run with Docker (recommended)

### All campaigns, all tasks
```bash
docker compose up --build
```

### Specific campaign + task
```bash
docker compose run --rm scraper --campaigns trump_2024 --task sentiment
docker compose run --rm scraper --campaigns españa_2023 --task stance
docker compose run --rm scraper --campaigns brexit_2016 trump_2016
```

### List available campaigns
```bash
docker compose run --rm scraper --list
```

---

## Run locally (without Docker)

```bash
pip install -r requirements.txt
python run.py --campaigns trump_2024 --task sentiment
python run.py  # all campaigns + all tasks
```

Requires `GOOGLE_APPLICATION_CREDENTIALS` set in environment or `.env`.

---

## Twitter account pool

`twscrape` uses a pool of Twitter accounts to scrape. More accounts = higher throughput and lower risk of rate limiting. Add accounts comma-separated in `.env`:

```env
TWITTER_ACCOUNTS=user1:pass1:email1@gmail.com:pass1,user2:pass2:email2@gmail.com:pass2
```

The account pool is stored in a local SQLite DB (`.twscrape/`) which is persisted via a Docker volume across runs — you won't need to re-login every time.

---

## Scraping parameters

| Variable | Default | Description |
|---|---|---|
| `MAX_TWEETS_PER_QUERY` | 500 | Max tweets per query |
| `MIN_LIKES` | 0 | Filter tweets below this like count |
| `INCLUDE_RETWEETS` | false | Include retweets |
| `TASK` | all | `sentiment` / `stance` / `all` |

---

## JSON schema

Output is a JSON array. Load in pandas with `pd.read_json("file.json")`.

```json
[{
  "id": "1234567890",
  "text": "Tweet content here",
  "created_at": "2023-07-20T10:30:00+00:00",
  "author_id": "987654321",
  "author_username": "user123",
  "lang": "es",
  "like_count": 42,
  "retweet_count": 10,
  "reply_count": 5,
  "quote_count": 2,
  "is_retweet": false,
  "hashtags": ["23j", "elecciones"],
  "campaign": "españa_2023",
  "task": "stance",
  "target": "psoe_sanchez",
  "query_slug": "españa_2023_psoe_sanchez_0",
  "collected_at": "2024-07-22T12:00:00+00:00"
}]
```

---

## Schedule on Google Cloud

To run periodically via Cloud Scheduler → Cloud Run Job:

```bash
# Build and push image
docker build -t gcr.io/YOUR_PROJECT/tfm-scraper .
docker push gcr.io/YOUR_PROJECT/tfm-scraper

# Create Cloud Run Job
gcloud run jobs create tfm-scraper \
  --image gcr.io/YOUR_PROJECT/tfm-scraper \
  --region europe-west1 \
  --set-env-vars GCS_BUCKET=my-tfm-bucket \
  --set-secrets TWITTER_ACCOUNTS=twitter-accounts:latest

# Schedule (e.g. daily at 03:00)
gcloud scheduler jobs create http tfm-scraper-daily \
  --schedule "0 3 * * *" \
  --uri "https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT/jobs/tfm-scraper:run" \
  --oauth-service-account-email YOUR_SA@YOUR_PROJECT.iam.gserviceaccount.com
```
