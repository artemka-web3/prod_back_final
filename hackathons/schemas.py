from .models import Hackathon
from ninja.orm import create_schema
from ninja import Schema
from  typing import List

HackathonSchema = create_schema(Hackathon)

class HackathonIn(Schema):
    name: str
    description: str
    participants: List[str]

class HackathonOut(Schema):
    creator: int
    name: str
    description: str
    participants: List[str]
    imave_cover: str
    min_participants: int 
    max_participants: int

class Error(Schema):
    details: str
    
