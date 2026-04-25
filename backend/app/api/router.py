from fastapi import APIRouter

from app.api.admin.upload_timetable import router as admin_router
from app.api.coverback import router as coverback_router
from app.api.employee.login import router as login_router
from app.api.employee.register import router as register_router
from app.api.employee.timetable import router as timetable_router
from app.api.swap.accept_reject_swap import router as accept_reject_router
from app.api.swap.find_swap import router as find_swap_router
from app.api.swap.history import router as swap_history_router
from app.api.swap.request_swap import router as request_swap_router

api_router = APIRouter()
api_router.include_router(register_router, prefix="/employee", tags=["Employee"])
api_router.include_router(login_router, prefix="/employee", tags=["Employee"])
api_router.include_router(timetable_router, prefix="/employee", tags=["Employee"])

api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])

api_router.include_router(find_swap_router, prefix="/swap", tags=["Swap"])
api_router.include_router(request_swap_router, prefix="/swap", tags=["Swap"])
api_router.include_router(accept_reject_router, prefix="/swap", tags=["Swap"])
api_router.include_router(swap_history_router, prefix="/swap", tags=["Swap"])

api_router.include_router(coverback_router, prefix="/coverback", tags=["Coverback"])
