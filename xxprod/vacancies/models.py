from django.db import models
from users.models import User


class Vacancy(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    team = models.ForeignKey(User, on_delete=models.CASCADE)
    

class Keyword(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete = models.CASCADE)
    text = models.CharField(max_length = 100, blank = False)
