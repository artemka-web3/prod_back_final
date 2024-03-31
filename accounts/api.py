from datetime import datetime

from django.http import Http404
from ninja import Router, Schema, Field
from django.contrib import auth
import jwt
from ninja.security import HttpBearer

from .models import Account
from .schemas import Token, UserSignin, UserProfile, Error
from xxprod.settings import SECRET_KEY


router = Router()

@router.post('/signup', response={201: UserProfile, 409: Error, 400: Error})
def signup(request, user: UserProfile):
    account = Account.objects.create_user(email=user.email, username=user.username, password=user.password, is_organizator=user.is_organizator)
    if user.age is not None:
        account.age = user.age
    if user.city is not None:
        account.city = user.city
    if user.work_experience is not None:
        account.city = user.work_experience
    account.save()
    return 201, account


@router.post('/signin', response={200: Token, 404: Error, 400: Error    })
def signup(request, user: UserSignin):
    account = auth.authenticate(username=user.username, password=user.password)
    if account is not None:
        encoded_jwt = jwt.encode({"createdAt": datetime.utcnow().timestamp(), "user_id": account.id}, SECRET_KEY, algorithm="HS256")
        return 200, {"token": encoded_jwt}
    else:
        raise Http404