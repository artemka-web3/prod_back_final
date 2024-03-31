from django.http import JsonResponse, Http404
from ninja import NinjaAPI
from accounts.api import router as accounts_router
from django.db.utils import IntegrityError

from authtoken import InvalidToken
from hackathons.api import hackathon_router, my_hackathon_router

api = NinjaAPI()

api.add_router("/auth/", accounts_router)
api.add_router('/hackathons/', hackathon_router)
api.add_router('/myhackathons/', my_hackathon_router)


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

@api.exception_handler(InvalidToken)
def invalid_token(request, exc):
    return api.create_response(
        request,
        {"details": "Provided token is not valid"},
        status=401
    )

@api.exception_handler(Http404)
def invalid_token(request, exc):
    return api.create_response(
        request,
        {"details": "Not found or data is not correct"},
        status=401
    )
