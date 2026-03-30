from enum import Enum


class RegistrationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ShiftName(str, Enum):
    MORNING = "MORNING"
    EVENING = "EVENING"
    NIGHT = "NIGHT"
    HOLIDAY = "HOLIDAY"
    OFF = "OFF"


class SwapType(str, Enum):
    DAILY = "DAILY"
    HOLIDAY = "HOLIDAY"


class SwapRequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class IntentStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
