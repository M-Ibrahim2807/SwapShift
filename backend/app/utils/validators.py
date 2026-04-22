import re

from app.core.exceptions import ValidationException


PHONE_REGEX = re.compile(r"^[0-9]{7,15}$")
PASSWORD_MIN_LENGTH = 8
SHIFT_TIME_REGEX = re.compile(r"^(\d{1,2})(?::?(\d{1,2}))?\s*(AM|PM)$", re.IGNORECASE)


def normalize_contact_number(value: str) -> str:
    normalized = re.sub(r"\D", "", value)
    if normalized.startswith("00"):
        normalized = normalized[2:]
    return normalized


def validate_contact_number(value: str) -> str:
    if not PHONE_REGEX.match(value):
        raise ValidationException("Invalid contact number format")
    return value


def validate_password(value: str) -> str:
    if len((value or "").strip()) < PASSWORD_MIN_LENGTH:
        raise ValidationException(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    return value


def canonicalize_shift_name(value: str) -> str:
    cleaned = " ".join((value or "").strip().upper().replace(".", ":").split())
    if not cleaned:
        raise ValidationException("Invalid shift_name: empty value")

    match = SHIFT_TIME_REGEX.match(cleaned)
    if not match:
        return cleaned

    hour = int(match.group(1))
    minutes = int(match.group(2) or 0)
    meridiem = match.group(3).upper()

    if not 1 <= hour <= 12 or not 0 <= minutes <= 59:
        return cleaned

    return f"{hour}:{minutes:02d} {meridiem}"


def normalize_shift_name(value: str) -> str:
    return canonicalize_shift_name(value)
