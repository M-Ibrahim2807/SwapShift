from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

SwapTypeLiteral = Literal["DAILY", "HOLIDAY"]
DailyModeLiteral = Literal["SINGLE_DAY", "MULTI_DAY"]
MeridiemLiteral = Literal["AM", "PM", "OFF"]


class DailySwapItem(BaseModel):
    date: date
    wanted_hour: int = Field(ge=1, le=12)
    wanted_meridiem: MeridiemLiteral


class FindSwapIn(BaseModel):
    swap_type: SwapTypeLiteral
    daily_mode: DailyModeLiteral | None = None
    target_date: date | None = None
    wanted_hour: int | None = Field(default=None, ge=1, le=12)
    wanted_meridiem: MeridiemLiteral | None = None
    multi_day_requests: list[DailySwapItem] | None = None

    @model_validator(mode="after")
    def validate_shape(self):
        if self.swap_type == "DAILY":
            if not self.daily_mode:
                raise ValueError("daily_mode required for DAILY")
            if self.daily_mode == "SINGLE_DAY":
                if not self.target_date or self.wanted_hour is None or not self.wanted_meridiem:
                    raise ValueError("target_date, wanted_hour, wanted_meridiem required for SINGLE_DAY")
                if self.multi_day_requests:
                    raise ValueError("multi_day_requests not allowed for SINGLE_DAY")
            if self.daily_mode == "MULTI_DAY":
                if not self.multi_day_requests:
                    raise ValueError("multi_day_requests required for MULTI_DAY")
                if not 2 <= len(self.multi_day_requests) <= 7:
                    raise ValueError("multi_day_requests must have between 2 and 7 days")
                if self.target_date or self.wanted_hour is not None or self.wanted_meridiem:
                    raise ValueError("target_date/wanted_* not allowed for MULTI_DAY")
        if self.swap_type == "HOLIDAY":
            if not self.target_date:
                raise ValueError("target_date required for HOLIDAY")
            if self.daily_mode or self.wanted_hour is not None or self.wanted_meridiem or self.multi_day_requests:
                raise ValueError("HOLIDAY only accepts target_date")
        return self


class MatchCandidateOut(BaseModel):
    employee_id: str
    name: str | None = None
    contact_number: str
    target_date: date
    swap_type: str
    requester_current_shift: str
    requester_wanted_shift: str
    candidate_current_shift: str


class DailyMatchGroupOut(BaseModel):
    date: date
    my_current_shift: str
    my_wanted_shift: str
    matches: list[MatchCandidateOut]


class FindSwapOut(BaseModel):
    matches: list[MatchCandidateOut] = []
    matches_by_date: list[DailyMatchGroupOut] | None = None


class CreateRequestIn(BaseModel):
    receiver_employee_id: str
    swap_type: SwapTypeLiteral
    target_date: date
    requester_current_shift: str
    receiver_current_shift: str
    expires_in_minutes: int = Field(default=360, ge=5, le=1440)


class SwapRequestOut(BaseModel):
    id: int
    requester_id: int
    receiver_id: int
    swap_type: str
    start_date: date
    end_date: date
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
