from ninja import Router
from typing import List
from .schemas import HackathonSchema, HackathonIn
from .models  import Hackathon
from accounts.models import Account
from ninja import UploadedFile, File


hackathon_router = Router()
my_hackathon_router = Router()


@hackathon_router.post('/') # if is authed else 409
def create_hackathon(request, payload: HackathonIn, image: UploadedFile = File(...)):
    payload_dict = payload.dict()
    hackathon = Hackathon(creator = request.user, name = payload_dict['name'], description = payload_dict['name'])
    hackathon.image_cover.save(image.name, image)
    for participant in payload_dict['participants']:
        # try except throw 401
        participant_acc = Account.objects.get(email=participant)
        hackathon.participans.add(participant_acc)
    return hackathon

@hackathon_router.get("/", response=List[HackathonSchema])
def list_hackathons(request):
    hackathons = Hackathon.objects.all()
    return hackathons

@my_hackathon_router.get("/", response=List[HackathonSchema])
def list_myhackathons(request):
    hackathons = Hackathon.objects.filter(creator__id = request.user).all()
    return hackathons