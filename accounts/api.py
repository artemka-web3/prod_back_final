from typing import Optional
from ninja import Router, Schema, Field


from .models import Account

class User(Schema):
    username: str = Field(..., min_length=1, max_length=30, required=True)
    email: str = Field(..., min_length=1, max_length=60, required=True)
    password: str = Field(..., min_length=6, required=True)
    is_organizator: bool
    age: Optional[int] = None
    city: Optional[str] = None
    work_experience: Optional[int] = None


class Error(Schema):
    details: str


router = Router()

@router.post('/signup', response={201: User, 409: Error, 400: Error})
def signup(request, user: User):
    account = Account.objects.create_user(email=user.email, username=user.username, password=user.password, is_organizator=user.is_organizator)
    if user.age is not None:
        account.age = user.age
    if user.city is not None:
        account.city = user.city
    if user.work_experience is not None:
        account.city = user.work_experience
    account.save()
    return 201, account



