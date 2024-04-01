from .models import Team
from ninja.orm import create_schema
from ninja import Schema
from typing import List
from pydantic import BaseModel

TeamSchema = create_schema(Team)




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
    id: int
    name: str
    email: str



class Successful(Schema):
    success: str


class Error(Schema):
    details: str


class SentEmail(Schema):
    link: str
    
class UserSuggesionForVacansionSchema(Schema):
    ids: List[int]