from .models import Team
from vacancies.models import Apply
from ninja.orm import create_schema
from ninja import Schema
from typing import List
from pydantic import BaseModel
from accounts.schemas import UserProfile

TeamSchema = create_schema(Team)


class ApplierSchema(Schema):
    applier_id: int
    vacancy_name: str


class Account(BaseModel):
    id: int
    email: str
    name: str



class TeamById(Schema):
    id: int
    hackathon: int
    name: str
    creator: int
    team_members: List[Account]





class VacancySchema(BaseModel):
    id: int
    name: str
    keywords: List[str]

class AddUserToTeam(Schema):
    email: str

class VacancySchemaOut(Schema):
    id: int
    name: str
    keywords: List[str]

class TeamSchemaOut(Schema):
    name: str
    vacancies: List[VacancySchema]

class TeamIn(Schema):
    name: str
    vacancies: List[VacancySchema]



class ApplyOut(Schema):
    applier_id: int
    vacancy_name: str



class Successful(Schema):
    success: str


class Error(Schema):
    details: str


class SentEmail(Schema):
    link: str
    
class UserSuggesionForVacansionSchema(Schema):
    users: List[UserProfile]

class VacansionSuggesionForUserSchema(Schema):
    vacantions: List[VacancySchema]