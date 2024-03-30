from django.db import models
from resumes.models import Resume


class SoftSkillTag(models.Model):
    resume = models.ForeignKey(Resume, on_delete = models.CASCADE)
    tag_text = models.CharField(max_length = 200, blank = False)
