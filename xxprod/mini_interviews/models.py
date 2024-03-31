from django.db import models
from users.models import User

class MiniInterview(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    description = models.TextField(blank = False)
    assigned_to = models.ForeignKey(User, on_delete = models.CASCADE) # потенциальный наемный сотрудник
    creator = models.ForeignKey(User, on_delete = models.CASCADE) # работадатель

class YesOrNoQ(models.Model):
    mini_interview = models.ForeignKey(MiniInterview, on_delete = models.CASCADE)
    q_text = models.CharField(max_length = 200, blank = False)
    answer =  models.BooleanField(default = False)

class CheckBoxQ(models.Model):
    mini_interview = models.ForeignKey(MiniInterview, on_delete = models.CASCADE)
    q_text = models.CharField(max_length = 200, blank = False)
    is_checked = models.BooleanField(default = False)

class TextQ(models.Model):
    mini_interview = models.ForeignKey(MiniInterview, on_delete = models.CASCADE)
    q_text = models.TextField(blank = False)
    q_answer = models.TextField(blank = False)


