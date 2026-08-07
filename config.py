# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- LLM API Configuration ----------
# Raise error if missing to prevent hardcoding keys in code/repo
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY not found. Please set it in .env file.")

# ---------- Feishu Bot Configuration ----------
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
if not FEISHU_WEBHOOK_URL:
    raise RuntimeError("FEISHU_WEBHOOK_URL not found. Please set it in .env file.")

# Feishu bot signature verification Secret (Optional)
# If signature verification is enabled in Feishu bot settings, set FEISHU_SECRET in .env
# Leave empty if disabled, signature verification will be skipped
FEISHU_SECRET = os.getenv("FEISHU_SECRET", "")

# ---------- SerpApi Configuration (for fetching job listings) ----------
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise RuntimeError("SERPAPI_KEY not found. Please set it in .env file.")

# ---------- Filter Conditions ----------
MATCH_SCORE_THRESHOLD = 75