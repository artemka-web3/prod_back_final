from ninja import Router
from typing import List
from resumes.models import Resume, SoftSkillTag, HardSkillTag
from .schemas import TeamIn, TeamSchema, Successful, Error, SentEmail, TeamSchemaOut, VacancySchemaOut, AddUserToTeam, ApplyOut, UserSuggesionForVacansionSchema, ApplierSchema, VacansionSuggesionForUserSchema, TeamById
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

@team_router.post('/accept_application', response={200: Successful}, auth = AuthBearer())
def accept_application(request, app_id):
    application = get_object_or_404(Apply, id = app_id)
    application.team.team_members.add(application.who_responsed)
    application.delete()
    return 200, {'success': 'ok'}

@team_router.post('/decline_application', response={200: Successful}, auth = AuthBearer())
def decline_application(request, app_id):
    application = get_object_or_404(Apply, id = app_id)
    application.delete()
    return 200, {'success': 'ok'}




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
                      f"https://prod.zotov.dev/join-team?vacancy_id={encoded_jwt}", 'sidnevar@yandex.ru',
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





@team_router.post('/join-team', auth = AuthBearer(), response={403: Error, 200: TeamSchema, 401: Error})
def join_team(request, team_id: int):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = get_object_or_404(Team, id=team_id)
    team.team_members.add(user)
    team.save()
    return 200, team


@team_router.patch('/edit_team', auth = AuthBearer(), response={200: TeamSchemaOut, 401: Error, 400: Error})
def edit_team(request, id: int, edited_team: TeamIn):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    team = get_object_or_404(Team, id=id)
    team.name = edited_team.name
    team.save()
    Vacancy.objects.filter(team=team).delete()
    vacancies = []
    for vacantion in edited_team.vacancies:
        vac = Vacancy.objects.create(name=vacantion.name, team=team)
        vacancies.append({
            'id': vac.id,
            'name': vac.name,
            'keywords': vacantion.keywords
        })
        for keyword in vacantion.keywords:
            Keyword.objects.create(vacancy=vac, text=keyword)

    team_to_return = {
        'name': team.name,
        'vacancies': vacancies
    }
    return 200, team_to_return


@team_router.get('/', response = {200: List[TeamSchema], 400: Error}, auth=AuthBearer())
def get_teams(request, hackathon_id):
    hackathon = get_object_or_404(Hackathon, id = hackathon_id)
    teams = Team.objects.filter(hackathon = hackathon).all()
    return 200, teams

@team_router.get('/team_vacancies', response={200: List[VacancySchemaOut]}, auth=AuthBearer())
def get_team_vacancies(request, id):
    team = Team.objects.filter(id = id).first()
    vacancies = Vacancy.objects.filter(team = team).all()
    vacancies_list = []
    for v in vacancies:
        keywords = Keyword.objects.filter(vacancy = v).all()
        keywords_l = []
        for i in keywords:
            keywords_l.append(i.text)
        vacancies_list.append({"id": v.id, 'name': v.name, 'keywords': keywords_l})
    return 200, vacancies_list

@team_router.get('/suggest_users_for_specific_vacansion/{vacansion_id}', response={200: UserSuggesionForVacansionSchema, 404: Error}, auth=AuthBearer())
def get_suggest_users_for_specific_vacansion(request, vacansion_id):
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    keywords = Keyword.objects.filter(vacancy_id = vacansion_id).all()
    vacancy = get_object_or_404(Vacancy, id=vacansion_id)
    matching = {}
    for user in Account.objects.all():
        if user.id == user_id:
            continue
        if user.is_organizator:
            continue
        else:
            count = 0
            try:
                resume = get_object_or_404(Resume, hackathon=vacancy.team.hackathon, user_id=user.id)
            except:
                matching[user.id] = 0
                continue
            teams = Team.objects.filter(hackathon=vacancy.team.hackathon)
            user_already_in_team = False
            for team in teams:
                if user in team.team_members.all():
                    user_already_in_team = True
            if user_already_in_team:
                continue
            softs = SoftSkillTag.objects.filter(resume = resume).all()
            softs_text = []
            for s in softs:
                softs_text.append(s.tag_text.lower())
            hards = HardSkillTag.objects.filter(resume = resume).all()
            hards_text = []
            for h in hards:
                hards_text.append(h.tag_text.lower())
            for keyword in keywords:
                if keyword.text.lower() in softs_text:
                    count += 1
                if keyword.text.lower() in hards_text:
                    count += 1
            matching[user.id] = count
    raiting = sorted(list(matching.items()), key= lambda x: list(x)[1], reverse=True)
    result = {'users': []}
    for i in raiting:
        result['users'].append(get_object_or_404(Account, id=int(list(i)[0])))
    return 200, result

@team_router.get('/suggest_vacansions_for_specific_user/{resume_id}', response={200: VacansionSuggesionForUserSchema, 404: Error}, auth=AuthBearer())
def get_suggest_vacansions_for_specific_user(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    softs = SoftSkillTag.objects.filter(resume=resume).all()
    hards = HardSkillTag.objects.filter(resume=resume).all()
    all_tags = []
    for soft in softs:
        all_tags.append(soft.tag_text.lower())
    for hard in hards:
        all_tags.append(hard.tag_text.lower())
    all_vacansions = Vacancy.objects.all()
    vacansions_matching = {}
    for vacansion in all_vacansions:
        keywords = Keyword.objects.filter(vacancy=vacansion).all()
        count = 0
        for keyword in keywords:
            if keyword.text.lower() in all_tags:
                count += 1
        vacansions_matching[vacansion.id] = count
    raiting = sorted(list(vacansions_matching.items()), key=lambda x: list(x)[1], reverse=True)
    result = {'vacantions': []}
    for i in raiting:
        vac = get_object_or_404(Vacancy, id=int(list(i)[0]))
        kws = [j.text for j in Keyword.objects.filter(vacancy=vac).all()]
        result['vacantions'].append({
            "id": vac.id,
            "name": vac.name,
            "keywords": kws
        })
    return 200, result



@team_router.post('/apply_for_job', auth=AuthBearer())
def apply_for_job(request, vac_id):
    vacancy = Vacancy.objects.filter(id = vac_id).first()
    team_owner_email = vacancy.team.creator.email
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    Apply.objects.create(vac = vacancy, team = vacancy.team, who_responsed = user)
    send_mail(f"{user.email} откликнулся на вакансию",
                      f"Посмотрите новый отклик", 'sidnevar@yandex.ru',
                      [team_owner_email], fail_silently=False)

@team_router.get("/get_applies_for_team", response={200: List[ApplierSchema]}, auth=AuthBearer())
def get_team_applies(request, team_id):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    team = Team.objects.filter(id = team_id).first()
    applies = Apply.objects.filter(team = team)
    applies_l = []
    for app in applies:
        applies_l.append({'id': app.id, 'team': app.team.id, 'vac': app.vac.id, 'who_responsed': app.who_responsed.id})
    return 200, applies_l


@team_router.get("/{team_id}", response = {200: TeamById}, auth=AuthBearer())
def get_team_by_id(request, team_id: int):
    team = get_object_or_404(Team, id = team_id)
    return 200, {'id': team.id, "hackathon": team.hackathon.id, "name": team.name, "creator": team.creator.id, 'team_members': [{'id': member.id, "email": member.email, "name": member.username} for member in team.team_members.all()]}

@team_router.post('/merge/{team1_id}/{team2_id}', response={200: TeamSchema, 401:Error, 400: Error, 404: Error}, auth=AuthBearer())
def merge_teams(request, team1_id:int, team2_id:int):
    team1 = get_object_or_404(Team, id=team1_id)
    team2 = get_object_or_404(Team, id=team2_id)
    team1.team_members.set(team1.team_members.all() | team2.team_members.all())
    team1.save()
    team2.delete()
    return 200, team1
