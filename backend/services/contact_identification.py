"""
Simplified Contact Identification Service
Relies on real_research output and stored targeting data—no paid enrichments.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..database.connection import DatabaseConnection
from ..models.schemas import ContactResponse, ContactSeniority
from .real_research import find_company_contacts, extract_targeting_criteria

logger = logging.getLogger(__name__)


class ContactIdentificationService:
    """Identify and persist key contacts for companies."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()

    async def identify_contacts(self, company_id: str) -> List[ContactResponse]:
        """
        Identify contacts for the given company and persist them.
        Returns whatever the research engine can find; no paid enrichment fallback.
        """
        company = await self._get_company(company_id)
        if not company:
            logger.warning("Cannot identify contacts: company %s not found", company_id)
            return []

        job = await self._get_job(company["job_id"])
        criteria = (job or {}).get("parameters") or {}
        if not criteria and job:
            criteria = await extract_targeting_criteria(job.get("prompt", ""))

        contacts: List[Dict[str, Any]] = await find_company_contacts(company, criteria)
        contacts = self._filter_contacts(contacts, criteria)

        if not contacts:
            logger.warning(
                "No contacts met targeting requirements for %s (%s)",
                company.get("name"),
                company.get("domain"),
            )
            return []

        stored: List[ContactResponse] = []
        for contact in contacts:
            record = await self._persist_contact(company_id, contact)
            if record:
                stored.append(record)

        return stored

    async def get_company_contacts(
        self,
        company_id: str,
    ) -> List[ContactResponse]:
        rows = await self.db.fetch_all(
            """
            SELECT *
            FROM contacts
            WHERE company_id = $1
            ORDER BY fit_score DESC, email_confidence DESC, created_at DESC
            """,
            company_id,
        )
        return [ContactResponse(**self._row_to_contact(row)) for row in rows]

    async def refresh_company_contacts(self, company_id: str) -> List[ContactResponse]:
        """
        Clear existing contacts for a company and re-run identification.
        """
        await self.db.execute("DELETE FROM contacts WHERE company_id = $1", company_id)
        return await self.identify_contacts(company_id)

    async def _persist_contact(
        self,
        company_id: str,
        contact: Dict[str, Any],
    ) -> Optional[ContactResponse]:
        """
        Store a contact record. Minimal validation is applied – we only require a name.
        """
        name = contact.get("name") or contact.get("full_name")
        first_name = contact.get("first_name")
        last_name = contact.get("last_name")

        if not (name or (first_name and last_name)):
            logger.debug("Skipping contact without identifiable name: %s", contact)
            return None

        if not first_name and name:
            parts = name.split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else None

        contact_id = str(uuid.uuid4())
        payload = {
            "id": contact_id,
            "company_id": company_id,
            "first_name": first_name,
            "last_name": last_name,
            "title": contact.get("title") or contact.get("position"),
            "email": contact.get("email"),
            "phone": contact.get("phone") or contact.get("phone_number"),
            "linkedin_url": contact.get("linkedin") or contact.get("linkedin_url"),
            "department": contact.get("department"),
            "seniority_level": self._infer_seniority(contact),
            "fit_score": float(contact.get("fit_score") or contact.get("confidence", 0.0) or 0.0),
            "email_confidence": float(contact.get("email_confidence") or contact.get("confidence", 0.0) or 0.0),
            "email_status": contact.get("email_status") or contact.get("status"),
            "verification_date": datetime.utcnow() if contact.get("email") else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await self.db.execute(
            """
            INSERT INTO contacts (
                id, company_id, first_name, last_name, title, email, phone,
                linkedin_url, department, seniority_level, fit_score,
                email_confidence, email_status, verification_date,
                created_at, updated_at
            )
            VALUES (
                $1, $2, $3, $4, $5, $6, $7,
                $8, $9, $10, $11,
                $12, $13, $14,
                $15, $16
            )
            ON CONFLICT (id) DO NOTHING
            """,
            payload["id"],
            payload["company_id"],
            payload["first_name"],
            payload["last_name"],
            payload["title"],
            payload["email"],
            payload["phone"],
            payload["linkedin_url"],
            payload["department"],
            payload["seniority_level"].value if payload["seniority_level"] else None,
            payload["fit_score"],
            payload["email_confidence"],
            payload["email_status"],
            payload["verification_date"],
            payload["created_at"],
            payload["updated_at"],
        )

        row = await self.db.fetch_one("SELECT * FROM contacts WHERE id = $1", contact_id)
        return ContactResponse(**self._row_to_contact(row))

    def _infer_seniority(self, contact: Dict[str, Any]) -> Optional[ContactSeniority]:
        """
        Guess the seniority level from the title.
        """
        title = (contact.get("title") or contact.get("position") or "").lower()
        if not title:
            return None

        if any(term in title for term in ["chief", "ceo", "founder", "president"]):
            return ContactSeniority.C_LEVEL
        if any(term in title for term in ["vp", "vice president", "executive", "partner"]):
            return ContactSeniority.VP
        if "director" in title:
            return ContactSeniority.DIRECTOR
        if "manager" in title:
            return ContactSeniority.MANAGER
        return ContactSeniority.INDIVIDUAL

    def _filter_contacts(
        self,
        contacts: List[Dict[str, Any]],
        criteria: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Deduplicate and enforce targeting rules for scraped contacts."""

        if not contacts:
            return []

        target_roles = []
        if criteria:
            target_roles = [role.lower() for role in criteria.get("target_roles", []) if role]

        role_keywords = set()
        for role in target_roles:
            role_keywords.update(role.split())

        def matches_target(contact_role: str) -> bool:
            if not role_keywords:
                return True
            contact_role = (contact_role or "").lower()
            return any(keyword in contact_role for keyword in role_keywords)

        seen_keys = set()
        filtered: List[Dict[str, Any]] = []

        for contact in contacts:
            role = contact.get("role") or contact.get("title") or ""
            name = contact.get("contact_name") or contact.get("name") or ""

            if not self._looks_like_person(name):
                continue

            if not matches_target(role):
                continue

            if not (contact.get("linkedin") or contact.get("email")):
                # Require at least one actionable field
                continue

            name_key = (contact.get("contact_name") or contact.get("name") or "").strip().lower()
            linkedin_key = (contact.get("linkedin") or "").strip().lower()
            email_key = (contact.get("email") or "").strip().lower()
            dedupe_key = (name_key, role.lower(), linkedin_key, email_key)

            if dedupe_key in seen_keys:
                continue

            seen_keys.add(dedupe_key)
            filtered.append(contact)

        return filtered

    def _looks_like_person(self, name: str) -> bool:
        if not name:
            return False

        lowered = name.lower()
        if any(keyword in lowered for keyword in [
            "team",
            "directory",
            "opportunity",
            "technology",
            "organization",
            "business",
            "company",
            "chart",
            "guide",
            "report",
            "writer",
            "copy",
            "marketing",
            "editor",
            "journalist",
        ]):
            return False

        parts = [p for p in re.split(r"[\s,]+", name) if p]
        if len(parts) < 2:
            return False

        valid_words = [p for p in parts if re.match(r"^[A-Za-z'.-]+$", p)]
        if len(valid_words) < 2:
            return False

        if name.isupper() or name.islower():
            return False

        return True

    async def _get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.fetch_one("SELECT * FROM companies WHERE id = $1", company_id)

    async def _get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.fetch_one("SELECT * FROM jobs WHERE id = $1", job_id)

    def _row_to_contact(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "company_id": row["company_id"],
            "first_name": row.get("first_name"),
            "last_name": row.get("last_name"),
            "title": row.get("title"),
            "email": row.get("email"),
            "phone": row.get("phone"),
            "linkedin_url": row.get("linkedin_url"),
            "department": row.get("department"),
            "seniority_level": row.get("seniority_level"),
            "fit_score": float(row.get("fit_score") or 0.0),
            "email_confidence": float(row.get("email_confidence") or 0.0),
            "email_status": row.get("email_status"),
            "verification_date": row.get("verification_date"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }
