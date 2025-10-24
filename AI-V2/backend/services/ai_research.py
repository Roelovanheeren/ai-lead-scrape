from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List
from urllib.parse import urlparse

from openai import OpenAI

from backend.core.settings import get_settings
from backend.utils.prompts import build_company_prompt
from backend.utils.validators import is_senior_title

logger = logging.getLogger(__name__)


def _parse_json(text: str) -> Any:
    if not text:
        return None
    start = None
    stack: List[str] = []
    pairs = {"[": "]", "{": "}"}

    for idx, ch in enumerate(text):
        if ch in pairs:
            if start is None:
                start = idx
            stack.append(pairs[ch])
        elif stack and ch == stack[-1]:
            stack.pop()
            if not stack and start is not None:
                snippet = text[start : idx + 1]
                try:
                    return json.loads(snippet)
                except json.JSONDecodeError:
                    continue
    return None


def _extract_domain(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


class AIResearchService:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_attempts = settings.max_lead_attempts
        self.min_leads_per_batch = settings.min_leads_per_batch

    def _call_openai(self, prompt: str) -> str:
        logger.info("Calling OpenAI with prompt length %s", len(prompt))
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": "You are a meticulous institutional investor research analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            tools=[{"type": "web"}],
        )
        return response.output_text

    async def generate_leads(self, user_prompt: str, target_count: int) -> List[Dict[str, Any]]:
        remaining = max(target_count, self.min_leads_per_batch)
        prompt = build_company_prompt(user_prompt, remaining)
        text = await asyncio.to_thread(self._call_openai, prompt)
        parsed = _parse_json(text)
        if not isinstance(parsed, list):
            logger.warning("AI response not list; prompt excerpt: %s", prompt[:200])
            return []

        leads: List[Dict[str, Any]] = []
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            company = (entry.get("company") or "").strip()
            if not company:
                continue
            contacts = entry.get("contacts") or []
            filtered_contacts = [c for c in contacts if is_senior_title(c.get("title"))]
            if not filtered_contacts:
                continue
            entry["contacts"] = filtered_contacts
            entry["domain"] = _extract_domain(entry.get("website"))
            leads.append(entry)

        logger.info("AI produced %s candidate companies", len(leads))
        return leads
