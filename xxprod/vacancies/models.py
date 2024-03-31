from django.db import models
from accounts.models import Account


class Vacancy(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    keywords = models.CharField(max_length = 200, blank = False)
    team = models.ForeignKey(User, on_delete=models.CASCADE)
    


