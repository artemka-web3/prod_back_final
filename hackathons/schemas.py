from accounts.models import Account
from profiles.schemas import UserProfile
from .models import Hackathon
from ninja.orm import create_schema
from ninja import Schema
from  typing import List

class HackathonSchema(Schema):
    id: int
    creator_id: int
    name: str
    image_cover: str
    description: str
    min_participants: int
    max_participants: int
    participants: List[UserProfile]

class HackathonIn(Schema):
    name: str
    description: str
    min_participants: int
    max_participants: int
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
    
