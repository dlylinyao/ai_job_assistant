# llm_engine.py
import json
import logging
from openai import OpenAI, RateLimitError, APIError
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    timeout=30.0  # Avoid indefinite hangs during network issues
)

# DeepSeek recommended to use deepseek-v4-flash for new projects
MODEL_NAME = "deepseek-v4-flash"

# Fallback result when model call fails or returns invalid format, ensuring main process won't crash due to a single job
DEFAULT_RESULT = {
    "score": 0,
    "reason": "Model call failed or returned invalid format. Job skipped.",
    "matched_skills": [],
    "missing_skills": [],
    "tailored_bullets": []
}


def evaluate_and_tailor_job(base_resume: str, job_title: str, jd_text: str) -> dict:
    prompt = f"""
You are a senior HR specialist familiar with the European (Finland/Nordics) recruitment market.
Please evaluate the match between the candidate's resume and the target job, and generate tailored work experience bullet points for this position.

Candidate Resume:
{base_resume}

Target Job Title: {job_title}
Target Job JD:
{jd_text}

Please strictly output in JSON format containing the following fields:
{{
  "score": match_score_integer_0_to_100,
  "reason": "brief evaluation reason",
  "matched_skills": ["matched skill 1", "skill 2"],
  "missing_skills": ["missing skill 1", "skill 2"],
  "tailored_bullets": ["tailored resume bullet 1", "bullet 2"]
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional HR specialist. Always respond in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
    except RateLimitError:
        # Let main.py catch and perform backoff retry; only raise it here
        logging.warning("⚠️ DeepSeek rate limit reached (429).")
        raise
    except APIError as e:
        logging.error(f"DeepSeek API call error: {e}")
        return DEFAULT_RESULT

    raw_content = response.choices[0].message.content

    try:
        result = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as e:
        logging.error(f"Failed to parse model JSON response: {e}\nRaw content: {raw_content}")
        return DEFAULT_RESULT

    # Fill in missing fields to avoid KeyError in main.py / feishu_notifier.py
    for key, default_value in DEFAULT_RESULT.items():
        result.setdefault(key, default_value)

    return result