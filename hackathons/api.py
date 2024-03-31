from ninja import Router
from typing import List
from .schemas import HackathonSchema, HackathonIn
from .models  import Hackathon
from accounts.models import Account
from ninja import UploadedFile, File
from authtoken import AuthBearer
from xxprod.settings import SECRET_KEY
from django.shortcuts import get_object_or_404
import jwt


hackathon_router = Router()
my_hackathon_router = Router()


@hackathon_router.post('/', auth = AuthBearer) # if is authed else 409
def create_hackathon(request, body: HackathonIn, image: UploadedFile = File(...)):
    body_dict = body.dict()
    hackathon = Hackathon(creator = request.user, name = body_dict['name'], description = body_dict['name'])
    hackathon.image_cover.save(image.name, image)
    for participant in body_dict['participants']:
        participant_acc = Account.objects.get(email=participant)
        hackathon.participans.add(participant_acc)
    return hackathon

@hackathon_router.get("/", response=List[HackathonSchema])
def list_hackathons(request):
    hackathons = Hackathon.objects.all()
    return hackathons

@my_hackathon_router.get("/", response=List[HackathonSchema])
def list_myhackathons(request):
    payload_dict = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload_dict['user_id']
    user = get_object_or_404(Account, id=user_id)
    hackathons = Hackathon.objects.filter(creator__id = request.user).all()
    return hackathons