from django.db import models

from babbles.models import Babble
from core.managers import DefaultManager
from core.utils import audio_file_path
from users.models import User


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    audio = models.FileField(upload_to=audio_file_path)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, blank=True)
    objects = DefaultManager()

    def __unicode__(self):
        return self.user.first_name
