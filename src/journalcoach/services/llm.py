# -*- coding: utf-8 -*-
import os
from typing import Callable, Tuple
from datetime import datetime
from openai import OpenAI
from ..config import env

class LLMService:
    def __init__(self) -> None:
        env.load_env()
        from ..secrets_loader import set_api_key_from_embedded_blob_if_available
        set_api_key_from_embedded_blob_if_available()
        self.client = OpenAI(api_key=env.get_api_key())
        self.model = env.get_model()

    def stream_questions(self, entry_text: str, on_delta: Callable[[str], None]) -> str:
        """
        Streams numbered follow-up questions in a journalistic tone.
        Returns the full questions text when complete.
        """
        system = (
            "You are a journal coach. Ask pointed, helpful follow-up questions about the user's daily journal entry. "
            "Keep a professional, journalistic tone. Number the questions like '1.', '2.', '3.'. "
            "Ask only questions. No preamble. No summary."
        )
        user = "Here is the journal entry:\n" + entry_text + "\n\nAsk numbered follow-up questions."

        stream = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=True,
        )

        full = []
        for event in stream:
            if getattr(event, "type", "") == "response.output_text.delta":
                delta = getattr(event, "delta", "")
                if delta:
                    on_delta(delta)
                    full.append(delta)
        return "".join(full)

    def summarize_and_clean(self, entry_text: str, questions: str, answers: str) -> Tuple[str, str]:
        """
        Returns (title, summary). Non-streaming.
        Includes today's local date in the inputs as requested.
        """
        today_local = datetime.now().strftime("%Y-%m-%d")

        system = (
            "You are a journal editor. Produce a cleaned, readable journal summary and a concise title. "
            "Return strictly in JSON with keys: title, summary."
        )
        user = (
            "Summarize and clean the user's daily journal entry.\n"
            "Include key accomplishments, lessons, and next-steps if implied.\n"
            "Inputs:\n"
            "- Local date: " + today_local + "\n"
            "- Original entry:\n" + entry_text + "\n"
            "- Follow-up questions:\n" + questions + "\n"
            "- User answers:\n" + answers + "\n"
            "Output JSON only."
        )

        resp = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = getattr(resp, "output_text", "") or ""
        import json
        import re
        m = re.search(r"\{.*\}", text, re.DOTALL)
        obj = json.loads(m.group(0)) if m else {"title": "Untitled", "summary": text.strip()}
        title = str(obj.get("title", "Untitled")).strip()
        summary = str(obj.get("summary", "")).strip()
        return title, summary
