"""
AI-assisted institutional investor discovery and contact enrichment.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from openai import OpenAI

from resources.hazen_road_research_guide import HAZEN_ROAD_GUIDE

logger = logging.getLogger(__name__)


def _parse_json_blocks(text: str) -> Any:
    """Extract the first JSON object/array from a text response."""
    if not text:
        return None
    start = None
    brackets = {"[": "]", "{": "}"}
    stack: List[str] = []
    for idx, ch in enumerate(text):
        if ch in brackets:
            if start is None:
                start = idx
            stack.append(brackets[ch])
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
    """Wrapper around OpenAI Responses API for Hazen Road research."""

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not configured for AI research service")
        self.client = OpenAI()
        self.model = model
        self.system_prompt = (
            HAZEN_ROAD_GUIDE.strip()
            + "\n\nYou are Hazen Road's institutional investor sourcing agent. "
            "You must follow the mission, scope, investor criteria, and output format exactly."
        )

    def _call_openai(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=messages,
            temperature=temperature,
            tools=[{"type": "web"}],
        )
        return response.output_text

    async def suggest_companies(
        self,
        prompt: str,
        target_count: int,
        excluded_domains: List[str],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Ask GPT to suggest new institutional investors and provide research snapshots."""
        instructions = f"""
Return JSON array of institutional investors that match Hazen Road's criteria.
Instructions:
- Only include investors that act as Limited Partners / co-invest in multifamily or build-to-rent.
- Prioritize Sunbelt activity, Opportunity Zone experience, and fund size $500M+ AUM.
- Exclude any company whose domain is in this list: {excluded_domains}.
- Each entry must look like:
{{
  "company": "...",
  "website": "https://...",
  "hq": "...",
  "aum": "...",
  "strategy_summary": "...",
  "alignment_score": 0-100,
  "reasons": ["..."],
  "sources": ["https://source1", "..."],
  "contacts": [
     {{
       "name": "...",
       "title": "...",
       "email": "... (if public, otherwise null)",
       "phone": "...",
       "linkedin": "https://linkedin.com/in/...",
       "confidence": 0-1
     }}
  ]
}}
- Provide at least {target_count} companies if possible.
- Contacts must be senior decision makers (Partner, Managing Director, VP, Head of Investments, etc.).
- If you cannot find enough, provide as many as possible with explicit explanations.
"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": instructions
                + "\nUse the following user prompt for context:\n"
                + (prompt or "Discover new institutional investors for Hazen Road."),
            },
        ]
        text = await asyncio.to_thread(self._call_openai, messages)
        parsed = _parse_json_blocks(text)
        if not isinstance(parsed, list):
            logger.warning("AI research returned non-list payload")
            return [], []

        companies: List[Dict[str, Any]] = []
        profiles: List[Dict[str, Any]] = []
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            website = entry.get("website")
            domain = _extract_domain(website)
            company_dict = {
                "name": entry.get("company"),
                "website": website,
                "domain": domain,
                "source": "AI Research",
                "description": entry.get("strategy_summary"),
                "discovery_score": entry.get("alignment_score", 0),
                "discovery_reasons": entry.get("reasons", []),
                "research_profile": entry,
            }
            companies.append(company_dict)
            profiles.append(entry)
        return companies, profiles

    async def fetch_contacts(
        self,
        company_name: str,
        website: Optional[str],
        max_contacts: int = 5,
    ) -> List[Dict[str, Any]]:
        """Use GPT to enumerate senior contacts when scraping fails."""
        if not company_name:
            return []
        instructions = f"""
Provide up to {max_contacts} senior decision makers at {company_name}.
Focus on titles like Partner, Managing Director, Head of Investments, Chief Investment Officer, VP Capital Markets, etc.
Return JSON array like:
[
  {{
     "name": "...",
     "title": "...",
     "email": "... (if public, otherwise null)",
     "phone": "...",
     "linkedin": "https://linkedin.com/in/...",
     "confidence": 0-1
  }}
]
If unsure, set confidence to 0.4 and leave email/phone null.
"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": instructions
                + "\nCompany website:"
                + (website or "Unknown"),
            },
        ]
        text = await asyncio.to_thread(self._call_openai, messages)
        parsed = _parse_json_blocks(text)
        if not isinstance(parsed, list):
            logger.warning("AI contacts response not list for %s", company_name)
            return []
        contacts: List[Dict[str, Any]] = []
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            contacts.append(entry)
        return contacts[:max_contacts]

    async def generate_leads(
        self,
        prompt: str,
        target_count: int,
        excluded_companies: List[str],
        excluded_contacts: List[str],
    ) -> List[Dict[str, Any]]:
        """Ask GPT (with browsing) to return structured investor leads."""
        instructions = f"""
Return a JSON array describing institutional investors that match Hazen Road's profile.
Requirements:
- Produce AT LEAST {target_count} distinct companies if possible.
- Exclude these companies (and their subsidiaries): {excluded_companies}.
- Contacts should be senior decision makers (Partner, Managing Director, VP Investments, Head of Capital Markets, CIO, etc.).
- Skip contacts whose names appear in this list: {excluded_contacts}.
- Each array element MUST follow this schema:
{{
  "company": "Legal company name",
  "website": "https://...",
  "hq": "City, State",
  "aum": "$X.XB" (if known),
  "strategy_summary": "1-2 sentences describing LP/BTR/OZ strategy",
  "alignment_score": 0-100,
  "reasons": ["Why this firm fits Hazen Road"],
  "sources": ["https://verified-source", ...],
  "contacts": [
     {{
       "name": "Full Name",
       "title": "Senior Title",
       "email": "email@company.com" or null,
       "phone": "+1-..." or null,
       "linkedin": "https://linkedin.com/in/..." or null,
       "confidence": 0-1
     }}
  ]
}}
- Prefer firms with Sunbelt build-to-rent / multifamily exposure, Opportunity Zone activity, and fund sizes that can write $5-50M equity checks.
- Always cite sources for company claims.
"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": instructions
                + "\nBase your research on reliable current sources. Use the following user brief for additional context:\n"
                + (prompt or "Discover institutional investors for Hazen Road."),
            },
        ]

        text = await asyncio.to_thread(self._call_openai, messages)
        parsed = _parse_json_blocks(text)
        if not isinstance(parsed, list):
            logger.warning("AI lead generation returned non-list payload")
            return []

        cleaned: List[Dict[str, Any]] = []
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            if not entry.get("company"):
                continue
            cleaned.append(entry)
        logger.info("AI lead generation produced %s companies", len(cleaned))
        return cleaned
