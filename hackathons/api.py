from datetime import datetime

from ninja import Router
from typing import List
from .schemas import HackathonSchema, HackathonIn
from .models  import Hackathon
from accounts.models import Account
from ninja import UploadedFile, File
from authtoken import AuthBearer
from xxprod.settings import SECRET_KEY
from django.shortcuts import get_object_or_404
from .schemas import Error, HackathonOut
from django.core.mail import send_mail
import jwt


hackathon_router = Router()
my_hackathon_router = Router()

@hackathon_router.post('/', auth = AuthBearer(), response={403: Error, 201: HackathonSchema, 401: Error}) # if is authed else 409
def create_hackathon(request, body: HackathonIn, image_cover: UploadedFile = File(...)):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)

    if user.is_organizator:
        body_dict = body.dict()
        hackathon = Hackathon(creator = user, name = body_dict['name'], description = body_dict['description'],
                              min_participants=body.min_participants, max_participants=body.max_participants)
        hackathon.save()
        hackathon.image_cover.save(image_cover.name, image_cover)
        for participant in body_dict['participants']:
            participant_acc = Account.objects.get(email=participant)
            if participant_acc:
                encoded_jwt = jwt.encode({"createdAt": datetime.utcnow().timestamp(), "id": hackathon.id}, SECRET_KEY, algorithm="HS256")
                try:
                    send_mail(f"Приглашение в хакатон {hackathon.name}",f"https://prod.zotov.dev/join-hackaton?hackathon_id={encoded_jwt}",'sidnevar@yandex.ru', [participant_acc.email], fail_silently=False)
                except: pass
        return 201, hackathon
    return 403, {'detail': "You are not organizator and you can't create hackathons"}

@hackathon_router.post('/join', auth = AuthBearer(), response={403: Error, 200: HackathonSchema, 401: Error})
def join_hackathon(request, hackathon_id: int):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)
    hackathon.participants.add(user)
    hackathon.save()
    return 200, hackathon

@hackathon_router.get("/", auth = AuthBearer(), response = {401: Error, 200: List[HackathonSchema]})
def list_hackathons(request):
    hackathons = Hackathon.objects.all()
    return 200, hackathons

@my_hackathon_router.get("/", auth = AuthBearer(), response = {401: Error, 200: List[HackathonSchema]})
def list_myhackathons(request):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    hackathons = Hackathon.objects.all()
    to_return = []
    for hack in hackathons:
        if hack.creator == user or user in hack.participants.all():
            to_return.append(hack)
    return 200, to_return