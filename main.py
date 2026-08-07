# main.py
import os
import time
import logging
from openai import RateLimitError

from config import FEISHU_WEBHOOK_URL, MATCH_SCORE_THRESHOLD
from job_fetcher import fetch_daily_jobs
from llm_engine import evaluate_and_tailor_job  # Core: Import only the merged evaluation function
from feishu_notifier import send_feishu_card

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Use absolute path based on script directory to avoid file not found errors when called from other working directories (e.g. cron or other launcher scripts)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_PATH = os.path.join(BASE_DIR, "base_resume.txt")


def main():
    # 1. Read base resume
    try:
        with open(RESUME_PATH, "r", encoding="utf-8") as f:
            base_resume = f.read()
    except FileNotFoundError:
        logging.error(f"Resume file not found: {RESUME_PATH}. Please prepare your base resume file first!")
        return

    # 2. Fetch daily job listings
    jobs = fetch_daily_jobs()
    logging.info(f"Successfully fetched {len(jobs)} jobs to evaluate.")

    # 3. Evaluate and process jobs one by one
    for index, job in enumerate(jobs):
        logging.info(f"[{index+1}/{len(jobs)}] Analyzing job: {job['title']} - {job['company']}")

        try:
            # A. Requires only 1 API call: get match score and tailored resume bullet points simultaneously
            result = evaluate_and_tailor_job(base_resume, job['title'], job['jd'])
            score = result.get('score', 0)
            logging.info(f"Job [{job['title']}] match score: {score}")

            # B. Push to Feishu if threshold is reached
            if score >= MATCH_SCORE_THRESHOLD:
                tailored_bullets = result.get('tailored_bullets', [])
                success = send_feishu_card(FEISHU_WEBHOOK_URL, job, result, tailored_bullets)
                if success:
                    logging.info(f"✅ Successfully pushed job [{job['title']}] to Feishu chat!")
                else:
                    logging.error("❌ Feishu card push failed.")
            else:
                logging.info(f"Low match job ({score} pts), automatically filtered out.")

        except RateLimitError:
            logging.warning("⚠️ DeepSeek rate limit reached. Pausing for 20 seconds before continuing to next job...")
            time.sleep(20)
        except Exception as e:
            logging.error(f"Unknown error occurred while processing job [{job['title']}]: {e}")

        # Pause for 3 seconds after analyzing each job to maintain a smooth API pacing
        time.sleep(3)


if __name__ == "__main__":
    main()