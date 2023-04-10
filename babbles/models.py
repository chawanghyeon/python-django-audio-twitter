from django.db import models

from core.managers import DefaultManager
from core.utils import audio_file_path
from tags.models import Tag
from users.models import User


class Babble(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio = models.FileField(upload_to=audio_file_path, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    like_count = models.IntegerField(default=0, blank=True, null=True)
    comment_count = models.IntegerField(default=0, blank=True, null=True)
    rebabble_count = models.IntegerField(default=0, blank=True, null=True)
    objects = DefaultManager()

    def __str__(self):
        return self.user.first_name
