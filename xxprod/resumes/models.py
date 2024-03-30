from django.db import models
from users.models import User
from hackathons.models import Hackathon

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    hackathon = models.ForeignKey(Hackathon, on_delete = models.CASCADE)
    personal_website = models.CharField(max_length = 200, blank = True)
    github = models.CharField(max_length = 200, blank = True)
    hhru = models.CharField(max_length = 200, blank = True)
    linkedin = models.CharField(max_length = 200, blank = True)
    # telegram = models.CharField(max_length = 200, blank = True)
    projects = models.TextField(blank = False) 
    




