from typing import Optional

SENIOR_TITLE_KEYWORDS = [
    "partner",
    "principal",
    "managing director",
    "director",
    "vice president",
    "svp",
    "head",
    "chief",
    "cio",
    "capital markets",
    "investment officer",
    "portfolio manager",
    "fund manager",
    "president",
]

REJECTED_TITLE_KEYWORDS = [
    "associate",
    "analyst",
    "assistant",
    "coordinator",
    "specialist",
    "consultant",
    "advisor",
    "marketing",
    "communications",
    "intern",
    "writer",
]


def is_senior_title(title: Optional[str]) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    if any(block in title_lower for block in REJECTED_TITLE_KEYWORDS):
        return False
    return any(keyword in title_lower for keyword in SENIOR_TITLE_KEYWORDS)
