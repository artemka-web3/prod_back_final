from django.db import models
from accounts.models import Account


class Hackathon(models.Model):
    creator = models.ForeignKey(Account, on_delete = models.CASCADE)
    name = models.CharField(max_length = 200, blank = False)
    image_cover = models.ImageField(upload_to = 'hackathon_images/')
    description = models.TextField(blank = False, default = 'описание хакатона')






