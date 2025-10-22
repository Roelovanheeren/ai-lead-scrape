"""
Institutional investor discovery pipeline for Hazen Road.
Builds targeted queries, pulls candidate firms, scores relevance.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Tuple

from .real_research import search_companies

logger = logging.getLogger(__name__)

BASE_SOURCE_QUERIES = [
    'site:rebusinessonline.com "fund" "build-to-rent"',
    'site:rebusinessonline.com "fund" "multifamily" "Sunbelt"',
    'site:connectcre.com "capital partner" "multifamily"',
    'site:connectcre.com "opportunity zone" "fund"',
    'site:globest.com "multifamily fund" "Sunbelt"',
    'site:urbanize.city "capital partner" "apartments"',
    'site:irei.com "fund closing" "multifamily"',
    'site:bisnow.com "capital partner" "build-to-rent"',
    '"launches opportunity zone fund" "multifamily"',
    '"closes" "multifamily fund" "limited partners"',
    '"commits capital" "multifamily" "build-to-rent"',
    '"institutional investor" "workforce housing" "Sunbelt"',
    '"qualified opportunity fund" "multifamily investor"',
    '"GP co-invest" "multifamily" "capital partners"',
]

LP_KEYWORDS = [
    "limited partner",
    "lp capital",
    "capital partner",
    "fund manager",
    "private equity",
    "investment management",
    "institutional investor",
    "commingled fund",
    "separate account",
]

BTR_KEYWORDS = [
    "build-to-rent",
    "btr",
    "single-family rental",
    "sfr",
    "multifamily",
    "workforce housing",
    "apartment community",
    "value-add multifamily",
]

OZ_KEYWORDS = [
    "opportunity zone",
    "qualified opportunity fund",
    "qof",
]

SUNBELT_KEYWORDS = [
    "phoenix",
    "arizona",
    "buckeye",
    "sunbelt",
    "texas",
    "florida",
    "georgia",
    "north carolina",
    "south carolina",
    "nevada",
    "tennessee",
    "alabama",
]

SCALE_KEYWORDS = [
    "aum",
    "assets under management",
    "billion",
    "million",
    "$",
    "fund ii",
    "fund iii",
    "fund iv",
    "fund v",
]

BLOCKED_DOMAINS = {
    "rebusinessonline.com",  # keep? we still want data but not final company
    "connectcre.com",
    "globest.com",
    "urbanize.city",
    "bisnow.com",
    "irei.com",
}


def _lower_text(*parts: str) -> str:
    return " ".join(part or "" for part in parts).lower()


def _score_company(result: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Return (score, reasons) if result looks like institutional investor; otherwise (0, [])."""
    text = _lower_text(result.get("name"), result.get("description"))
    domain = (result.get("domain") or "").lower()

    if not text:
        return 0, []

    reasons: List[str] = []
    score = 0

    if any(keyword in text for keyword in LP_KEYWORDS):
        score += 4
        reasons.append("LP language detected")

    if any(keyword in text for keyword in BTR_KEYWORDS):
        score += 3
        reasons.append("BTR/multifamily focus")

    if any(keyword in text for keyword in OZ_KEYWORDS):
        score += 2
        reasons.append("Opportunity Zone involvement")

    if any(keyword in text for keyword in SUNBELT_KEYWORDS):
        score += 2
        reasons.append("Sunbelt presence")

    if any(keyword in text for keyword in SCALE_KEYWORDS):
        score += 1
        reasons.append("Institutional scale marker")

    # domain heuristics – block known news sites unless they also have strong LP signals
    if domain in BLOCKED_DOMAINS and score < 7:
        return 0, []

    # require at least two distinct reasons to qualify
    if len(reasons) < 2 or score < 5:
        return 0, []

    return score, reasons


async def discover_investor_companies(
    prompt: str,
    targeting_criteria: Dict[str, Any],
    target_count: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Discover institutional investors aligned with Hazen Road thesis.

    Returns:
        (qualified_companies, diagnostics)
    """
    custom_queries = list(BASE_SOURCE_QUERIES)

    industry_keywords = targeting_criteria.get("keywords") or []
    for keyword in industry_keywords[:5]:
        custom_queries.append(f'"{keyword}" "capital partner" "multifamily"')
        custom_queries.append(f'"{keyword}" "limited partner" "real estate"')

    criteria = {
        "prompt": prompt or "Hazen Road build-to-rent institutional investor discovery",
        "keywords": targeting_criteria.get("keywords", []),
        "industry": targeting_criteria.get("industry", "Real Estate Investment"),
        "location": targeting_criteria.get("location", "Sunbelt"),
        "custom_queries": custom_queries,
    }

    raw_results = await search_companies(criteria, max(target_count * 6, 40))
    logger.info(f"Investor discovery pulled {len(raw_results)} raw results")

    qualified: List[Dict[str, Any]] = []
    diagnostics: List[Dict[str, Any]] = []

    for result in raw_results:
        score, reasons = _score_company(result)
        diagnostics.append(
            {
                "name": result.get("name"),
                "domain": result.get("domain"),
                "score": score,
                "reasons": reasons,
                "snippet": result.get("description"),
            }
        )
        if score > 0:
            result = dict(result)
            result["discovery_score"] = score
            result["discovery_reasons"] = reasons
            qualified.append(result)

    deduped: Dict[str, Dict[str, Any]] = {}
    for res in qualified:
        key = res.get("domain") or res.get("website") or res.get("name")
        if not key:
            continue
        if key not in deduped or res.get("discovery_score", 0) > deduped[key].get("discovery_score", 0):
            deduped[key] = res

    qualified = list(deduped.values())
    qualified.sort(key=lambda r: r.get("discovery_score", 0), reverse=True)
    diagnostics.sort(key=lambda r: r.get("score", 0), reverse=True)

    return qualified[: max(target_count, 10)], diagnostics[:50]
