from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_employee_id(self, employee_id: str) -> Employee | None:
        return self.db.scalar(select(Employee).where(Employee.employee_id == employee_id))

    def get_by_pk(self, pk: int) -> Employee | None:
        return self.db.scalar(select(Employee).where(Employee.id == pk))

    def create(self, employee_id: str, contact_number: str, contact_hash: str) -> Employee:
        employee = Employee(
            employee_id=employee_id,
            contact_number=contact_number,
            contact_hash=contact_hash,
            is_active=False,
            registration_status="PENDING",
        )
        self.db.add(employee)
        self.db.flush()
        return employee

    def list_pending(self) -> list[Employee]:
        return list(self.db.scalars(select(Employee).where(Employee.registration_status == "PENDING")))

    def save(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.flush()
        return employee
