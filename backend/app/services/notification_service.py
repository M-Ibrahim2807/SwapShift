from app.models.employee import Employee


class NotificationService:
    def notify_swap_request(self, receiver: Employee, request_id: int) -> None:
        # Placeholder for SMS/Email/Push integration.
        print(f"[notify] employee={receiver.employee_id} has new swap request={request_id}")
