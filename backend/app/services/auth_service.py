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
        
        # Use generic message for security (don't reveal if ID exists or not)
        if employee is None or not verify_password(payload.password, employee.contact_hash):
            raise AuthException("Invalid employee ID or password")
        
        if not employee.is_active:
            raise AuthException("Account is not active. Please contact administrator.")

        token = create_access_token(payload.employee_id, role="employee")
        return TokenOut(access_token=token)

    def admin_login(self, payload: AdminLoginIn) -> TokenOut:
        if payload.username != self.settings.admin_username or payload.password != self.settings.admin_password:
            raise AuthException("Invalid username or password")
        token = create_access_token(payload.username, role="admin")
        return TokenOut(access_token=token)
