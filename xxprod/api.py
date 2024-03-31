from django.http import JsonResponse
from ninja import NinjaAPI
from accounts.api import router as accounts_router
from django.db.utils import IntegrityError

api = NinjaAPI()

api.add_router("/auth/", accounts_router)

@api.exception_handler(IntegrityError)
def integruty_error(request, exc):
    return api.create_response(
        request,
        {"details": f"Already exist: {exc}"},
        status=409
    )

@api.exception_handler(ValueError)
def value_error(request, exc):
    return api.create_response(
        request,
        {"details": f"Value is not valid: {exc}"},
        status=400
    )
