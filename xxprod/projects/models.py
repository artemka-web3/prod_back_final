from django.db import models


class Project(models.Model):
    name = models.CharField(max_length = 200, blank = False)
    image_cover = models.ImageField(upload_to = 'project_images/')
    description = models.TextField(blank = False)






