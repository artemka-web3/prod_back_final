from ninja import Router, Schema, Field
from typing import Optional, List

from projects.schemas import Project


class Resume(Schema):
    bio: str = Field(..., min_length=1, required=True)
    hackathon_id: int
    tech: Optional[List[str]] = None
    soft: Optional[List[str]] = None
    github: Optional[str] = ''
    hh: Optional[str] = ''
    telegram: Optional[str] = ''
    personal_website: Optional[str] = ''
    pdf_link: Optional[str] = ''

class Error(Schema):
    details: str
