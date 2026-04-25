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


class TimetableSource(str, Enum):
    ADMIN = "ADMIN"
    MANUAL = "MANUAL"


class CoverbackType(str, Enum):
    OFFER = "OFFER"
    FIND = "FIND"


class CoverbackStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
