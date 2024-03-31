from django.db import models
from accounts.models import Account
from hackathons.models import Hackathon

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    hackathon = models.ForeignKey(Hackathon, on_delete = models.CASCADE)
    personal_website = models.CharField(max_length = 200, blank = True)
    github = models.CharField(max_length = 200, blank = True)
    hhru = models.CharField(max_length = 200, blank = True)
    linkedin = models.CharField(max_length = 200, blank = True)
    telegram = models.CharField(max_length = 200, blank = True)
    pdf = models.FileField(upload_to='resumes/')

    
    
class HardSkillTag(models.Model):
    resume = models.ForeignKey(Resume, on_delete = models.CASCADE)
    tag_text = models.CharField(max_length = 100, blank = False)


class SoftSkillTag(models.Model):
    resume = models.ForeignKey(Resume, on_delete = models.CASCADE)
    tag_text = models.CharField(max_length = 200, blank = False)


