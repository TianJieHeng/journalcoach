# JournalCoach

Tkinter app to:
1) Type a daily journal entry.
2) Get numbered follow-up questions (streamed).
3) Answer them.
4) Get a cleaned summary and title, then save to JSONL.

## Setup (Windows, cmd.exe)

python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
Edit .env:


OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
RATE_LIMIT_PER_MINUTE=30

python -m journalcoach.app
First run
Click Choose JSONL to pick or create your journal file.

Write your entry in the Input box.

Click Ask Questions. Questions stream into the Return box.

Type your answers back into the Input box.

Click Summarize & Save. The app writes a JSONL record with:

date_local (YYYY-MM-DD)

time_gmt_iso (UTC timestamp)

title

summary

A .bak backup is created before each append.

Notes
Uses OpenAI Responses API with streaming.

Model and API key are read from environment variables via .env in development.

No icons. Window is resizable. API calls run in background threads.

Rate limiting and simple retry logic are included.

Packaging and private API key
For development, use .env. For your private EXE later:

You can embed a DPAPI-encrypted blob and decrypt at runtime to set OPENAI_API_KEY in memory.

Do not distribute the EXE if it contains secrets.