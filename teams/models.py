from django.db import models
from accounts.models import Account


class Team(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    creator = models.ForeignKey(Account, on_delete = models.CASCADE)
    


