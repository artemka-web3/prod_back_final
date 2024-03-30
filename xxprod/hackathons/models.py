from django.db import models


class Hackathon(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    image_cover = models.ImageField(upload_to = 'hackathon_images/')






