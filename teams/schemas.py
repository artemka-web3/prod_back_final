from .models import Team
from ninja.orm import create_schema
from ninja import Schema
from  typing import List

TeamSchema = create_schema(Team)

class TeamIn(Schema):
    name: str
    creator_id: int
    vacancies_ids: List[int]


class Successful(Schema):
    success: str


class Error(Schema):
    details: str


class SentEmail(Schema):
    link: str
    
