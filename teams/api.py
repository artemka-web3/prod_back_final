from ninja import Router
from typing import List
from .schemas import TeamIn, TeamSchema, Successful, Error, SentEmail, TeamSchemaOut, VacancySchemaOut, AddUserToTeam, ApplyOut
from .models import Team
from vacancies.models import Vacancy, Keyword, Apply
from django.shortcuts import  get_object_or_404
from accounts.models import Account
import jwt
from authtoken import AuthBearer
from xxprod.settings import SECRET_KEY
from datetime import datetime
from django.core.mail import send_mail
from hackathons.models import Hackathon

team_router = Router()


@team_router.post("/create", auth = AuthBearer(), response={201: TeamSchemaOut})
def create_team(request, hackathon_id: int, body: TeamIn):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    body_dict = body.dict()
    hackathon = get_object_or_404(Hackathon, id = hackathon_id)
    team = Team(hackathon = hackathon, name = body_dict['name'], creator = user)
    team.save()
    for v in body_dict['vacancies']:
        vacancy = Vacancy(team = team, name = v['name'])
        vacancy.save()
        for kw in v['keywords']:
            Keyword.objects.create(vacancy = vacancy, text = kw) 
    vacancies = Vacancy.objects.filter(team = team).all()
    vacancies_l = []
    for v in vacancies:
        keywords = Keyword.objects.filter(vacancy = v).all()
        keywords_l = [k.text for k in keywords]
        vacancies_l.append({"id":v.id,'name': v.name, 'keywords': keywords_l})
    team_return = {'name': team.name, 'vacancies': vacancies_l}   
    return 201, team_return

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


@team_router.post("/{team_id}/add_user", auth = AuthBearer(), response = {201: TeamSchema, 401: Error, 404: Error, 403: Error, 400: Error})
def add_user_to_team(request, team_id: int, email_schema: AddUserToTeam):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    me_id = payload_dict['user_id']
    me = get_object_or_404(Account, id=me_id)
    team = get_object_or_404(Team, id=team_id)
    try:
        user_to_add = Account.objects.get(email=email_schema.email)
    except:
        user_to_add = None
    if team.creator == me:
        if user_to_add and team.creator == user_to_add:
            return 400, {'details': 'user is creator team'}
        encoded_jwt = jwt.encode({"createdAt": datetime.utcnow().timestamp(), "id": team.id}, SECRET_KEY,
                                 algorithm="HS256")
        try:
            send_mail(f"Приглашение в команду {team.name}",
                      f"https://prod.zotov.dev/join-team?team_id={encoded_jwt}", 'sidnevar@yandex.ru',
                      [email_schema.email], fail_silently=False)
        except:
            pass
        return 201, team
    else:
        return 403, {'details': "You are not creator and you can't edit this hackathon"}

@team_router.delete("/{team_id}/remove_user", auth = AuthBearer(), response = {201: TeamSchema, 401: Error, 404: Error, 403: Error, 400: Error})
def remove_user_from_team(request, team_id: int, email_schema: AddUserToTeam):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    me_id = payload_dict['user_id']
    me = get_object_or_404(Account, id=me_id)
    team = get_object_or_404(Team, id=team_id)
    user_to_remove = get_object_or_404(Account, email=email_schema.email)
    if team.creator == me:
        if user_to_remove != team.creator:
            if user_to_remove in team.team_members.all():
                team.team_members.remove(user_to_remove)
                team.save()
            return 201, team
        else:
            return 400, {'detail': "This user is creator of team"}
    else:
        return 403, {'detail': "You are not creator and you can't edit this team"}





@team_router.post('/join_team', auth = AuthBearer(), response={403: Error, 200: TeamSchema, 401: Error})
def join_team(request, vacancy_id: int):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    vac = get_object_or_404(Vacancy, id=vacancy_id)
    team = vac.team
    team.team_members.add(user)
    team.save()
    return 200, team


@team_router.patch('/edit_team', auth = AuthBearer(), response={200: TeamSchemaOut, 401: Error, 400: Error})
def edit_team(request, id, edited_team: TeamIn):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = get_object_or_404(Team, id=id)
    edited_team_dict = edited_team.dict()
    if team.creator == user:
        new_name = edited_team_dict['name']
        team.name = new_name
        for vac in edited_team_dict['vacancies']:
            # existing vac
            vacancy = Vacancy.objects.filter(id = vac['id']).first()
            if vacancy:
                print('exist')
                keywords = Keyword.objects.filter(vacancy = vacancy).all().delete()
                edited_keywords = vac['keywords']
                for kw in edited_keywords:
                    Keyword.objects.create(vacancy = vacancy, text = kw)
            else:
                v = Vacancy(team = team, name = vac['name'])
                v.save()
                keyws = vac['keywords']
                for k in keyws:
                    Keyword.objects.create(vacancy = v, text = k) 
                print('not exist')

        all_vacs = Vacancy.objects.filter(team = team).all()
        all_vacs_l = []
        edited_vacs_list = edited_team_dict['vacancies']
        for v in all_vacs:
            all_vacs_l.append(v.id)
        to_delete_vacs = set(all_vacs_l - edited_vacs_list)
        for v in to_delete_vacs:
            Vacancy.objects.filter(id = v.id).delete()

        vacancies_l = []
        for v in all_vacs:
            keywords = Keyword.objects.filter(vacancy = v).all()
            keywords_l  = []
            for i in keywords:
                keywords_l.append(i.text)
            vacancies_l.append({"id": v.id,'name': v.name, 'keywords': keywords_l})
        team_return = {'name': team.name, 'vacancies': vacancies_l}   
        return 200, team_return
    else:
        return 400, {'details': 'you are not the owner of this team so you cant edit this'}
    
@team_router.get('/', response = {200: List[TeamSchema], 400: Error})
def get_teams(request, hackathon_id):
    hackathon = get_object_or_404(Hackathon, id = hackathon_id)
    teams = Team.objects.filter(hackathon = hackathon).all()
    return 200, teams

@team_router.get('/team_vacancies', response={200: List[VacancySchemaOut]})
def get_team_vacancies(request, id):
    team = Team.objects.filter(id = id).first()
    vacancies = Vacancy.objects.filter(team = team).all()
    vacancies_list = []
    for v in vacancies:
        keywords = Keyword.objects.filter(vacancy = v).all()
        keywords_l  = []
        for i in keywords:
            keywords_l.append(i.text)
        vacancies_list.append({"id": v.id, 'name': v.name, 'keywords': keywords_l})
    return 200, vacancies_list


@team_router.post('/apply_for_job')
def apply_for_job(request, vac_id):
    vacancy = Vacancy.objects.filter(id = vac_id).first()
    team_owner_email = vacancy.team.creator.email
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    send_mail(f"{user.email} откликнулся на вакансию",
                      f"Посмотрите новый отклик", 'sidnevar@yandex.ru',
                      [team_owner_email], fail_silently=False)

@team_router.get("/get_applies_for_team", response={200: List[ApplyOut]})
def get_team_applies(request, vacancy_id):
    vacancy = Vacancy.objects.filter(id = vacancy_id).first()
    applies = Apply.objects.filter(vacancy = vacancy)
    return 200, applies


@team_router.get("/{team_id}", response={200: TeamSchema})
def get_team_by_id(request, team_id: int):
    team = get_object_or_404(Team, id = team_id)

    return 200, team