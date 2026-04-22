import logging
from app.models.employee import Employee
from app.utils.whatsapp_redirect import build_whatsapp_link

logger = logging.getLogger(__name__)


class NotificationService:
    def notify_swap_request(self, receiver: Employee, request_id: int) -> None:
        """Send a WhatsApp notification to the receiver about a new swap request."""
        try:
            if not receiver.contact_number:
                logger.warning(f"No contact number for employee {receiver.employee_id}")
                return
            
            whatsapp_link = build_whatsapp_link(receiver.contact_number)
            message = f"You have a new shift swap request! Request ID: {request_id}. Check the app to accept or reject it."
            
            logger.info(
                f"Swap request notification",
                extra={
                    "receiver_id": receiver.employee_id,
                    "request_id": request_id,
                    "contact": receiver.contact_number,
                    "whatsapp_link": whatsapp_link,
                    "notification_text": message,
                }
            )
            
            # In production, you would integrate with:
            # - Twilio for SMS/WhatsApp API
            # - Firebase Cloud Messaging for push notifications
            # - SendGrid for email notifications
            
            print(f"[notify] employee={receiver.employee_id} has new swap request={request_id}")
            print(f"[whatsapp_link] {whatsapp_link}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
