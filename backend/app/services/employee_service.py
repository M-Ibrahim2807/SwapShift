from sqlalchemy.orm import Session

from app.core.constants import RegistrationStatus
from app.core.exceptions import ValidationException
from app.core.security import get_password_hash
from app.repositories.coverback_repo import CoverbackRepository
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.request_repo import RequestRepository
from app.repositories.swap_history_repo import SwapHistoryRepository
from app.repositories.swap_repo import SwapRepository
from app.repositories.timetable_repo import TimetableRepository
from app.schemas.employee_schema import RegisterIn
from app.utils.validators import normalize_contact_number, validate_contact_number, validate_password


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.coverback_repo = CoverbackRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.request_repo = RequestRepository(db)
        self.swap_repo = SwapRepository(db)
        self.timetable_repo = TimetableRepository(db)
        self.swap_history_repo = SwapHistoryRepository(db)

    def register(self, payload: RegisterIn):
        normalized_contact = normalize_contact_number(payload.contact_number)
        validate_contact_number(normalized_contact)
        validate_password(payload.password)

        employee = self.employee_repo.get_by_employee_id(payload.employee_id)
        if employee is None:
            employee = self.employee_repo.create(
                employee_id=payload.employee_id,
                contact_number=normalized_contact,
                contact_hash=get_password_hash(payload.password),
            )
            message = "Your timetable does not exist yet. Your registration requires admin approval."
        else:
            employee.contact_number = normalized_contact
            employee.contact_hash = get_password_hash(payload.password)
            employee.registration_status = RegistrationStatus.APPROVED.value
            employee.is_active = True
            self.employee_repo.save(employee)
            message = "Registration successful. Your account is activated."

        self.db.commit()
        return employee, message

    def list_pending_registrations(self):
        return self.employee_repo.list_pending()

    def list_all_employees(self):
        return self.employee_repo.list_all()

    def approve_registration(self, employee_id: str):
        employee = self.employee_repo.get_by_employee_id(employee_id)
        if employee is None:
            raise ValidationException("Employee not found")
        employee.registration_status = RegistrationStatus.APPROVED.value
        employee.is_active = True
        self.employee_repo.save(employee)
        self.db.commit()
        return employee

    def reject_registration(self, employee_id: str):
        employee = self.employee_repo.get_by_employee_id(employee_id)
        if employee is None:
            raise ValidationException("Employee not found")
        employee.registration_status = RegistrationStatus.REJECTED.value
        employee.is_active = False
        self.employee_repo.save(employee)
        self.db.commit()
        return employee

    def delete_employee(self, employee_id: str):
        employee = self.employee_repo.get_by_employee_id(employee_id)
        if employee is None:
            raise ValidationException("Employee not found")

        self.coverback_repo.delete_all_for_employee(employee.id)
        self.swap_history_repo.delete_all_for_employee(employee.id)
        self.request_repo.delete_all_for_employee(employee.id)
        self.timetable_repo.delete_all_for_employee(employee.id)
        self.employee_repo.delete(employee)
        self.db.commit()
        return {"employee_id": employee_id, "message": "Employee deregistered successfully"}
