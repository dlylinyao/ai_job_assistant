# job_fetcher.py (with freshness filtering and status check)
import logging
import requests
from serpapi import GoogleSearch

from config import SERPAPI_KEY


def is_job_active(url: str) -> bool:
    """Quickly check if a job posting is still active.

    If the network request fails, keep the job by default (instead of marking it invalid),
    avoiding accidental removal due to temporary network issues; closed jobs will be handled
    by keyword matching below and fallback filtering in fetch_daily_jobs().
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        res = requests.get(url, headers=headers, timeout=6)
        if "No longer accepting applications" in res.text:
            return False
        return True
    except requests.RequestException as e:
        logging.warning(f"Failed to check job status, keeping job temporarily: {url} (Reason: {e})")
        return True


def fetch_daily_jobs() -> list:
    params = {
        "engine": "google",
        "q": 'site:linkedin.com/jobs/view/ "Helsinki" ("Junior" OR "Trainee" OR "Intern") ("AI" OR "Data" OR "NLP" OR "Analytics")',
        "tbs": "qdr:w",  # Only get jobs posted in the last 7 days
        "hl": "en",
        "num": "15",     # Fetch extra items for filtering
        "api_key": SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        if "error" in results:
            logging.error(f"SerpApi error: {results['error']}")
            return []

        organic_results = results.get("organic_results", [])

        real_jobs = []
        for index, item in enumerate(organic_results):
            job_url = item.get("link", "")
            raw_title = item.get("title", "N/A")
            snippet = item.get("snippet", "")

            # 1. Text keyword check
            dead_keywords = ["no longer accepting applications", "closed", "expired"]
            if any(kw in snippet.lower() for kw in dead_keywords):
                continue

            # 2. Webpage status check
            if not is_job_active(job_url):
                logging.info(f"⏩ Automatically skipping closed job: {raw_title}")
                continue

            clean_title = (
                raw_title.replace(" | LinkedIn", "")
                         .replace(" - LinkedIn", "")
                         .replace("hiring in Finland", "")
                         .strip()
            )

            real_jobs.append({
                "id": f"linkedin_job_{index}",
                "title": clean_title,
                "company": "LinkedIn Listed Company",
                "location": "Finland",
                "salary": "See Job Description",
                "url": job_url,
                "jd": f"Job Title: {clean_title}\nJob Summary: {snippet}"
            })

            # Collect at most 10 valid jobs
            if len(real_jobs) >= 10:
                break

        logging.info(f"🔍 Successfully filtered {len(real_jobs)} latest valid LinkedIn jobs!")
        return real_jobs

    except Exception as e:
        logging.error(f"An error occurred during request: {e}")
        return []