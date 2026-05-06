"""
SECURITY: PII redactor
PURPOSE: Redact PII before sending anything to Acontext.
ENCODING: UTF-8 WITHOUT BOM

- Mask emails
- Mask phone numbers
- Mask personal names if confidence > 0.8
"""

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Patterns for PII detection
_EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)
_PHONE_PATTERN = re.compile(
    r"(?:\+?[\d\s\-()]{10,20}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b)",
)

# Common PII keys to redact recursively
_PII_KEYS = frozenset({
    "email", "emails", "e_mail", "e-mail",
    "phone", "phones", "phone_number", "phoneNumber", "mobile", "fax",
    "contact_email", "contact_phone", "contact_email_address",
    "first_name", "firstName", "last_name", "lastName", "full_name", "fullName",
    "person_name", "contact_name", "recipient_name",
    "address", "street", "street_address", "postal_address",
    "ssn", "tax_id", "national_id", "passport",
})


def _mask_email(s: str) -> str:
    """Mask email: keep first 2 chars and domain, e.g. jo***@example.com."""
    match = _EMAIL_PATTERN.search(s)
    if not match:
        return s
    email = match.group(0)
    parts = email.split("@")
    if len(parts) != 2:
        return "[REDACTED]"
    local, domain = parts
    if len(local) <= 2:
        masked_local = local[0] + "***" if local else "***"
    else:
        masked_local = local[:2] + "***"
    return masked_local + "@" + domain


def _mask_phone(s: str) -> str:
    """Mask phone: show last 4 digits only."""
    match = _PHONE_PATTERN.search(s)
    if not match:
        return s
    phone = match.group(0)
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 4:
        return "***" + digits[-4:]
    return "[REDACTED]"


def _mask_personal_name(value: str, confidence: float = 0.0) -> str:
    """
    Mask personal name if confidence > 0.8.
    Simple heuristic: if it looks like "First Last" or single capitalized word.
    """
    if confidence < 0.8:
        return value
    if not value or not isinstance(value, str):
        return value
    v = value.strip()
    if not v:
        return value
    parts = v.split()
    if len(parts) == 1:
        return v[0] + "***" if len(v) > 1 else "***"
    return parts[0][0] + "*** " + (parts[-1][0] + "***" if len(parts) > 1 else "")


def _redact_value(value: Any, pii_key: bool = False, name_confidence: float = 0.0) -> Any:
    """Redact a single value."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        s = value
        s = _EMAIL_PATTERN.sub(lambda m: _mask_email(m.group(0)), s)
        s = _PHONE_PATTERN.sub(lambda m: _mask_phone(m.group(0)), s)
        if pii_key and name_confidence >= 0.8 and s and len(s) > 1 and s[0].isupper():
            s = _mask_personal_name(s, name_confidence)
        return s
    if isinstance(value, list):
        return [_redact_value(v, pii_key, name_confidence) for v in value]
    if isinstance(value, dict):
        return redact_payload(value, name_confidence)
    return value


def redact_payload(payload: dict, name_confidence: float = 0.0) -> dict:
    """
    Redact PII from payload before sending to Acontext.
    - Mask emails
    - Mask phone numbers
    - Mask personal names if confidence > 0.8
    """
    if not isinstance(payload, dict):
        return payload
    out: Dict[str, Any] = {}
    for k, v in payload.items():
        k_lower = k.lower() if isinstance(k, str) else ""
        pii_key = any(p in k_lower for p in _PII_KEYS) or k_lower in _PII_KEYS
        out[k] = _redact_value(v, pii_key=pii_key, name_confidence=name_confidence)
    return out
