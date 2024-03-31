from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja import Router
from django.contrib import auth
import jwt
from authtoken import AuthBearer

from accounts.models import Account
from .schemas import UserProfile, Error
from xxprod.settings import SECRET_KEY


router = Router()

@router.get('/profile', response={200: UserProfile, 401: Error}, auth=AuthBearer())
def profile(request):
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Account, id=user_id)
    return 200, user

@router.get('/profiles/user_id', response={200: UserProfile, 401: Error, 404: Error}, auth=AuthBearer())
def profiles(request, user_id:int):
    user = get_object_or_404(Account, id=user_id)
    return 200, user
