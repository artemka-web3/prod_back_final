from ninja import Router
from typing import List
from .schemas import TeamIn, TeamSchema
from .models import Team
from vacancies.models import Vacancy, Keyword
from django.shortcuts import  get_object_or_404
from accounts.models import Account
import jwt
from authtoken import AuthBearer
from xxprod.settings import SECRET_KEY
from datetime import datetime


team_router = Router()


@team_router.post("/create", auth = AuthBearer())
def create_team(request, body: TeamIn):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = Team(name = body['name'], creator = user)
    for vacancy in body['vacancies_ids']:
        vacancy = Vacancy.objects.create(team = team, name = vacancy['name'])
        for kw in vacancy['keywords']:
            Keyword.objects.create(vacancy = vacancy, text = kw)    
    return team

@team_router.delete("/delete", auth = AuthBearer())
def delete_team(request, id):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = get_object_or_404(Team, id = user_id)
    team.delete()
    return {'success': True}

@team_router.post('/invite-user')
def invite_user(request, id):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)

    encoded_jwt = jwt.encode({"createdAt": datetime.utcnow().timestamp(), "id": id}, SECRET_KEY, algorithm="HS256")
    # user = get_object_or_404(Account, id = decoded_id)

    email = user.email


    


