from django.db import models


class Team(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    team_leader = models.IntegerField(blank = False)
    


