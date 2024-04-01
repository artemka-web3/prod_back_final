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
from .schemas import Error, HackathonOut, EditHackathon, AddUserToHack
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

@hackathon_router.post("/{hackathon_id}/add_user", auth = AuthBearer(), response = {201: HackathonSchema, 401: Error, 404: Error, 403: Error, 400: Error})
def add_user_to_hackathon(request, hackathon_id: int, email_schema: AddUserToHack):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    me_id = payload_dict['user_id']
    me = get_object_or_404(Account, id=me_id)
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)
    try:
        user_to_add = Account.objects.get(email=email_schema.email)
    except:
        user_to_add = None
    if hackathon.creator == me:
        if user_to_add and hackathon.creator == user_to_add:
            return 400, {'details': 'user is creator hackathon'}
        encoded_jwt = jwt.encode({"createdAt": datetime.utcnow().timestamp(), "id": hackathon.id}, SECRET_KEY,
                                 algorithm="HS256")
        try:
            send_mail(f"Приглашение в хакатон {hackathon.name}",
                      f"https://prod.zotov.dev/join-hackaton?hackathon_id={encoded_jwt}", 'sidnevar@yandex.ru',
                      [email_schema.email], fail_silently=False)
        except:
            pass
        return 201, hackathon
    else:
        return 403, {'details': "You are not creator and you can't edit this hackathon"}

@hackathon_router.delete("/{hackathon_id}/remove_user", auth = AuthBearer(), response = {201: HackathonSchema, 401: Error, 404: Error, 403: Error, 400: Error})
def remove_user_from_hackathon(request, hackathon_id: int, email_schema: AddUserToHack):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    me_id = payload_dict['user_id']
    me = get_object_or_404(Account, id=me_id)
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)
    user_to_remove = get_object_or_404(Account, email=email_schema.email)
    if hackathon.creator == me:
        if user_to_remove != hackathon.creator:
            if user_to_remove in hackathon.participants.all():
                hackathon.participants.remove(user_to_remove)
                hackathon.save()
            return 201, hackathon
        else:
            return 400, {'detail': "This user is creator of hackathon"}
    else:
        return 403, {'detail': "You are not creator and you can't edit this hackathon"}

@hackathon_router.patch('/{id}', auth=AuthBearer(), response={200:HackathonSchema, 401:Error, 400:Error, 403: Error, 404: Error})
def edit_hackathons(request, hackothon_edit: EditHackathon, id:int):
    hackathon = get_object_or_404(Hackathon, id=id)
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    if hackathon.creator == user:
        if hackothon_edit.name:
            hackathon.name = hackothon_edit.name
            hackathon.save()
        if hackothon_edit.description:
            hackathon.description = hackothon_edit.description
            hackathon.save()
        if hackothon_edit.min_participants:
            hackathon.min_participants = hackothon_edit.min_participants
            hackathon.save()
        if hackothon_edit.max_participants:
            hackathon.max_participants = hackothon_edit.max_participants
            hackathon.save()
        return 200, hackathon
    else:
        return 403, {'detail': "You are not creator and you can't edit this hackathons"}

@hackathon_router.get('/{id}', auth=AuthBearer(), response={200:HackathonSchema, 401:Error, 400:Error, 404: Error})
def get_specific_hackathon(request, id:int):
    hackathon = get_object_or_404(Hackathon, id=id)
    return 200, hackathon

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