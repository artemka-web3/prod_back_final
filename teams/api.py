from ninja import Router
from typing import List
from .schemas import TeamIn, TeamSchema
from .models import Team
from vacancies.models import Vacancy, Keyword


team_router = Router()


@team_router.post("/create")
def create_team(request, payload: TeamIn):
    payload_dict = payload.dict()
    team = Team(name = payload_dict['name'], creator = request.user)
    for vacancy in payload_dict['vacancies_ids']:
        vacancy = Vacancy.objects.create(team = team, name = vacancy['name'])
        for kw in vacancy['keywords']:
            Keyword.objects.create(vacancy = vacancy, text = kw)    
    return team

    


