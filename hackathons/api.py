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
import jwt


hackathon_router = Router()
my_hackathon_router = Router()


@hackathon_router.post('/', auth = AuthBearer(), response={403: Error, 201: HackathonOut, 401: Error}) # if is authed else 409
def create_hackathon(request, body: HackathonIn, image_cover: UploadedFile = File(...)):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)

    if user.is_organizator:
        body_dict = body.dict()
        hackathon = Hackathon(creator = user, name = body_dict['name'], description = body_dict['description'])
        hackathon.save()
        hackathon.image_cover.save(image_cover.name, image_cover)
        for participant in body_dict['participants']:
            participant_acc = Account.objects.get(email=participant)
            hackathon.participants.add(participant_acc.email)
        return 201, hackathon
    return 403, {'detail': "You are not organizator and you can't create hackathons"}

@hackathon_router.get("/", auth = AuthBearer(), response = {401: Error, 200: List[HackathonSchema]})
def list_hackathons(request):
    hackathons = Hackathon.objects.all()
    return 200, hackathons

@my_hackathon_router.get("/", auth = AuthBearer(), response = {401: Error, 200: List[HackathonSchema]})
def list_myhackathons(request):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    hackathons = Hackathon.objects.filter(creator = user).all()
    return 200, hackathons