from app.config import get_settings
from sqlalchemy.orm import Session

from app.core.exceptions import AuthException
from app.core.security import create_access_token, verify_password
from app.repositories.employee_repo import EmployeeRepository
from app.schemas.employee_schema import AdminLoginIn, LoginIn, TokenOut
from app.utils.validators import validate_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.settings = get_settings()

    def login(self, payload: LoginIn) -> TokenOut:
        validate_password(payload.password)
        employee = self.employee_repo.get_by_employee_id(payload.employee_id)
        if employee is None:
            raise AuthException("Employee not found")
        if not employee.is_active:
            raise AuthException("Account is not active")
        if not verify_password(payload.password, employee.contact_hash):
            raise AuthException("Invalid credentials")

        token = create_access_token(payload.employee_id, role="employee")
        return TokenOut(access_token=token)

    def admin_login(self, payload: AdminLoginIn) -> TokenOut:
        if payload.username != self.settings.admin_username or payload.password != self.settings.admin_password:
            raise AuthException("Invalid admin credentials")
        token = create_access_token(payload.username, role="admin")
        return TokenOut(access_token=token)
