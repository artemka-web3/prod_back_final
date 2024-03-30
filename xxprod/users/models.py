from django.db import models
from hackathons.models import Hackathon
from projects.models import Project



class User(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    email = models.EmailField(max_length = 200, unique = True, blank = False)
    password = models.CharField(max_length = 200, blank = False)
    age = models.IntegerField(blank = True)
    city = models.CharField(max_length = 100, blank = True)
    work_exp = models.IntegerField(blank = True)
    role = models.CharField(max_length = 100,  blank = False)
    hackathons = models.ManyToManyField(Hackathon)
    teams = models.ManyToManyField(Project)




