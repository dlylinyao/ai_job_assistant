# AI Job Assistant 🎯

An automated pipeline that finds relevant job postings, scores them against your resume using an LLM, generates tailored resume bullet points for each match, and pushes high-fit opportunities straight to a Feishu (Lark) chat — so you only spend time on jobs worth applying to.

## The Problem

Job hunting in a niche field (AI/NLP roles in a specific country, in my case) means manually checking new postings every day, reading through job descriptions, judging fit, and rewriting resume bullets to match each role's language. That's a lot of repetitive manual work for a handful of genuinely relevant postings per day.

This tool automates that loop end-to-end.

## How It Works

```
┌──────────────┐     ┌──────────────────┐     ┌───────────────────┐     ┌──────────────┐
│  Fetch jobs   │ --> │  LLM evaluation   │ --> │  Score >= threshold │ --> │  Push to chat │
│ (search API)  │     │ (match score +    │     │        ?           │     │ (Feishu card) │
│               │     │  tailored bullets)│     │                     │     │              │
└──────────────┘     └──────────────────┘     └───────────────────┘     └──────────────┘
```

1. **`job_fetcher.py`** — Searches for recently posted, still-open job listings matching target keywords and location.
2. **`llm_engine.py`** — Sends the job description and base resume to an LLM in a single call, which returns a structured JSON with a match score, matched/missing skills, and resume bullet points rewritten for that specific role.
3. **`main.py`** — Orchestrates the pipeline, filters out low-scoring matches, and handles rate limiting.
4. **`feishu_notifier.py`** — Sends an interactive card with the score, reasoning, and tailored bullets to a Feishu group chat, with a direct link to apply.

## Tech Stack

- **Python 3**
- **LLM API** (DeepSeek, OpenAI-compatible) — prompt engineering + structured JSON output
- **SerpApi** — job listing discovery
- **Feishu (Lark) Webhook** — interactive card notifications
- **python-dotenv** — environment-based configuration

## Features

- 🔍 Automatically discovers new job postings on a schedule
- 🧠 LLM-based match scoring (0–100) with clear reasoning
- ✍️ Auto-generates resume bullet points tailored to each job description
- 🔔 Real-time push notifications with a direct apply link
- ⚙️ Configurable match-score threshold to control notification volume
- 🛡️ Rate-limit handling and graceful failure recovery

## Getting Started

### Prerequisites

- Python 3.10+
- A [DeepSeek API key](https://platform.deepseek.com) (or any OpenAI-compatible LLM API)
- A [SerpApi key](https://serpapi.com)
- A Feishu custom bot webhook URL ([setup guide](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot))

### Installation

```bash
git clone https://github.com/<your-username>/ai-job-assistant.git
cd ai-job-assistant
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and fill in your own keys:

```bash
cp .env.example .env
```

```env
DEEPSEEK_API_KEY=your_deepseek_key
SERPAPI_KEY=your_serpapi_key
FEISHU_WEBHOOK_URL=your_feishu_webhook_url
FEISHU_SECRET=            # optional, only if signature verification is enabled
```

> ⚠️ Never commit your `.env` file. It's already excluded via `.gitignore`.

Add your resume as plain text to `base_resume.txt` in the project root.

### Usage

```bash
python main.py
```

Run it manually, or schedule it as a daily cron job / GitHub Action to check for new postings automatically.

## Example Output

*(Add a screenshot or GIF of the Feishu card notification here)*

## Roadmap

- [ ] Support additional job sources beyond LinkedIn search results
- [ ] Add a lightweight web dashboard to review matches
- [ ] Support multiple resume versions for different role types

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## About

Built by [Linyao Du](https://www.linkedin.com/in/linyao-du-77317a2b4) — M.A. candidate in Language Technology at the University of Helsinki, exploring practical applications of LLMs and NLP.

Currently open to Data Scientist / AI / NLP opportunities in Finland and the Nordics. Feel free to connect!