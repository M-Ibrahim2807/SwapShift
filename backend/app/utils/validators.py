import re

from app.core.exceptions import ValidationException


PHONE_REGEX = re.compile(r"^[0-9]{7,15}$")
PASSWORD_MIN_LENGTH = 8


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


def normalize_shift_name(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise ValidationException("Invalid shift_name: empty value")
    return normalized
