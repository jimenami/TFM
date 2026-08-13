"""
CLI entry point for the Twitter scraper.

Usage:
    python run.py                                  # all campaigns, all tasks
    python run.py --campaigns brexit_2016          # one campaign
    python run.py --campaigns trump_2024 españa_2023 --task sentiment
    python run.py --list                           # list available campaigns
"""
import argparse
import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from political_queries import CAMPAIGNS
from scraper import run_scraper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Twitter political campaign scraper → GCS")
    parser.add_argument(
        "--campaigns",
        nargs="+",
        choices=list(CAMPAIGNS.keys()),
        default=None,
        help="Campaigns to scrape (default: all)",
    )
    parser.add_argument(
        "--task",
        choices=["sentiment", "stance", "all"],
        default="all",
        help="Task type to scrape (default: all)",
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        default=None,
        help="Stance target slugs to scrape, e.g. sumar_diaz (default: all)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available campaigns and exit",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        print("Available campaigns:")
        for slug, camp in CAMPAIGNS.items():
            print(f"  {slug:<20} {camp['label']}  [{camp['since']} → {camp['until']}]  lang={camp['lang']}")
        sys.exit(0)

    results = asyncio.run(run_scraper(campaigns=args.campaigns, task=args.task, targets=args.targets))

    total = sum(results.values())
    print(f"\nScraping complete — {total} tweets collected across {len(results)} queries")


if __name__ == "__main__":
    main()
