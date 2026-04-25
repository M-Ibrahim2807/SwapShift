from datetime import datetime

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    employee_id: str = Field(min_length=2, max_length=50)
    contact_number: str = Field(min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class RegisterOut(BaseModel):
    employee_id: str
    is_active: bool
    registration_status: str
    message: str


class LoginIn(BaseModel):
    employee_id: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class AdminLoginIn(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmployeeOut(BaseModel):
    name: str | None = None
    supervisor_name: str | None = None
    employee_id: str
    contact_number: str
    is_active: bool
    registration_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DeleteEmployeeOut(BaseModel):
    employee_id: str
    message: str
