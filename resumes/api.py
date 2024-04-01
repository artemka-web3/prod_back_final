from typing import Optional

from django.shortcuts import get_object_or_404
from ninja import Router, UploadedFile, File
import jwt

from accounts.models import Account
from authtoken import AuthBearer
from hackathons.models import Hackathon
from xxprod.settings import SECRET_KEY
from .models import Resume, HardSkillTag, SoftSkillTag
from .schemas import Error
from .schemas import Resume as ResumeSchema

router = Router()


@router.post('/create/custom', response={201: ResumeSchema, 401:Error, 400: Error, 404: Error, 409: Error}, auth=AuthBearer())
def create_resume_custom(request, resume: ResumeSchema):
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    hackathon = get_object_or_404(Hackathon, id=resume.hackathon_id)
    account = get_object_or_404(Account, id=user_id)
    resume_found = Resume.objects.filter(user=account, hackathon=hackathon)
    if len(list(resume_found)) > 0:
        return 409, {"details": "Resume already exists"}
    resume_created = Resume.objects.create(bio=resume.bio, hackathon=hackathon, user=account)
    if resume.tech is not None:
        for tag in resume.tech:
            HardSkillTag.objects.create(
                resume=resume_created,
                tag_text=tag
            )
    if resume.soft is not None:
        for tag in resume.soft:
            SoftSkillTag.objects.create(
                resume=resume_created,
                tag_text=tag
            )
    if resume.github != '':
        resume_created.github = resume.github
        resume_created.save()
    if resume.hh != '':
        resume_created.hhru = resume.hh
        resume_created.save()
    if resume.telegram != '':
        resume_created.telegram = resume.telegram
        resume_created.save()
    if resume.personal_website != '':
        account = get_object_or_404(Account, id=user_id)
        resume_created.user = account
        resume_created.save()
    result = resume.dict().copy()
    return 201,result

@router.post('/create/pdf', response={201: ResumeSchema, 401: Error, 400: Error, 404: Error, 409: Error},auth=AuthBearer())
def create_resume_pdf_upload(request, resume: ResumeSchema, pdf: UploadedFile = File(...)):
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    hackathon = get_object_or_404(Hackathon, id=resume.hackathon_id)
    account = get_object_or_404(Account, id=user_id)
    resume_created = Resume.objects.filter(user=account, hackathon=hackathon)
    result = {}
    resume_created.pdf.save(pdf.name, pdf)
    result['pdf_link'] = resume_created.pdf
    result['bio'] = resume_created.bio
    result['hackathon_id'] = resume_created.hackathon.id
    result['github'] = resume_created.github
    result['hh'] = resume_created.hhru
    result['telegram'] = resume_created.telegram
    result['personal_website'] = resume_created.personal_website
    result['pdf_link'] = resume_created.pdf
    techs = HardSkillTag.objects.filter(resume=resume_created)
    ss = SoftSkillTag.objects.filter(resume=resume_created)
    hards = []
    softs = []
    for tech in techs:
        hards.append(tech.tag_text)
    for soft in ss:
        softs.append(soft.tag_text)
    result['tech'] = hards
    result['soft'] = softs
    return 200, result

@router.get('/get', response={200: ResumeSchema, 401:Error, 400: Error, 404: Error}, auth=AuthBearer())
def get_resume(request, user_id: int, hackathon_id:int):
    user = get_object_or_404(Account, id=user_id)
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)
    resume = get_object_or_404(Resume, user=user, hackathon=hackathon)
    result = {}
    result['bio'] = resume.bio
    result['hackathon_id'] = resume.hackathon.id
    result['github'] = resume.github
    result['hh'] = resume.hhru
    result['telegram'] = resume.telegram
    result['personal_website'] = resume.personal_website
    result['pdf_link'] = resume.pdf
    techs = HardSkillTag.objects.filter(resume=resume)
    ss = SoftSkillTag.objects.filter(resume=resume)
    hards = []
    softs = []
    for tech in techs:
        hards.append(tech.tag_text)
    for soft in ss:
        softs.append(soft.tag_text)
    result['tech'] = hards
    result['soft'] = softs
    return 200, result

@router.patch('/edit', response={200: ResumeSchema, 401:Error, 400: Error, 404: Error}, auth=AuthBearer())
def edit_resume(request, resume: ResumeSchema):
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    hackathon = get_object_or_404(Hackathon, id=resume.hackathon_id)
    account = get_object_or_404(Account, id=user_id)
    resume_created = get_object_or_404(Resume, user=account, hackathon=hackathon)
    if resume.tech is not None:
        HardSkillTag.objects.filter(resume=resume_created).delete()
        for tag in resume.tech:
            HardSkillTag.objects.create(
                resume=resume_created,
                tag_text=tag
            )
    if resume.soft is not None:
        SoftSkillTag.objects.filter(resume=resume_created).delete()
        for tag in resume.soft:
            SoftSkillTag.objects.create(
                resume=resume_created,
                tag_text=tag
            )
    if resume.github != '':
        resume_created.github = resume.github
        resume_created.save()
    if resume.bio != '':
        resume_created.bio = resume.bio
        resume_created.save()
    if resume.hh != '':
        resume_created.hhru = resume.hh
        resume_created.save()
    if resume.telegram != '':
        resume_created.telegram = resume.telegram
        resume_created.save()
    if resume.personal_website != '':
        resume_created.personal_website = resume.personal_website
        resume_created.save()
    result = resume.dict().copy()
    return 200,result