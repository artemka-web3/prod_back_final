from ninja import Router
from typing import List
from .schemas import TeamIn, TeamSchema, Successful, Error, SentEmail
from .models import Team
from vacancies.models import Vacancy, Keyword
from django.shortcuts import  get_object_or_404
from accounts.models import Account
import jwt
from authtoken import AuthBearer
from xxprod.settings import SECRET_KEY
from datetime import datetime
from django.core.mail import send_mail


team_router = Router()


@team_router.post("/create", auth = AuthBearer(), response={201: List[TeamSchema]})
def create_team(request, body: TeamIn):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = Team(name = body['name'], creator = user)
    for v in body['vacancies']:
        vacancy = Vacancy.objects.create(team = team, name = v['name'])
        for kw in v['keywords']:
            Keyword.objects.create(vacancy = vacancy, text = kw)    
    return team

@team_router.delete("/delete", auth = AuthBearer(), response={201: Successful, 400: Error,  401: Error})
def delete_team(request, id):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = get_object_or_404(Team, id = id)
    if team.creator == user:
        team.delete()
        return 201, {'success': 'ok'}
    else:
        return 400, {'details': 'You cant delete team where you are not owner'}

@team_router.post('/invite_user', auth = AuthBearer(), response={401: Error, 400: Error, 201: SentEmail})
def invite_user(request, team_id: int, invited_user_id: int):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    invited_user = Account.objects.get(id = invited_user_id) 
    encoded_jwt = jwt.encode({"createdAt": datetime.utcnow().timestamp(), "id": team_id}, SECRET_KEY, algorithm="HS256")
    team = Team.objects.get(id = team_id)
    if team.creator == user:
        send_mail("Приглашение в команду", f"(ссылка не та) http://158.160.116.151:8000/accept-invitation?team_id_hash={encoded_jwt}", 'sidnevar@yandex.ru', [invited_user.email], fail_silently=False)
        return 201, {'link': f"http://158.160.116.151:8000/accept-invitation?team_id_hash={encoded_jwt}"}
    else:
        return 400, {'details': 'you are not the owner of this team'}


@team_router.post('/accept-invitation', auth = AuthBearer(), response={401: Error, 400: Error, 201: Successful})
def accept_invitation(request, team_id_hash: str):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    decoded_id = jwt.decode(team_id_hash, SECRET_KEY, algorithms=["HS256"])
    team = get_object_or_404(Team, id = decoded_id)
    team.team_members.add(user)
    return 201, {'status': 'ok'}


@team_router.patch('edit_team/', auth = AuthBearer(), response={201: List[TeamSchema]})
def edit_team(request, id, edited_team: TeamIn):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = get_object_or_404(Team, id=id)
    edited_team_dict = edited_team.dict()
    if team.creator == user:
        team.name = edited_team_dict['name']
        for v in edited_team_dict['vacancies']:
            vacancy = Vacancy.objects.create(team = team, name = v['name'])
            for kw in v['keywords']:
                Keyword.objects.create(vacancy = vacancy, text = kw) 
        return 201, team
    else:
        return 401, {'details':  "you are not allowed to edit team"}




    


