from django.contrib.auth.models import AbstractUser
from django.db import models

from core.managers import PrivateUserManager
from core.utils import image_file_path


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True, unique=True)
    birthday = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to=image_file_path, blank=True, null=True)
    background = models.ImageField(upload_to=image_file_path, blank=True, null=True)
    nickname = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=20, blank=True)
    number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    bio = models.CharField(max_length=140, blank=True)
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    objects = PrivateUserManager()

    def __unicode__(self):
        return self.first_name

    def __str__(self):
        return self.first_name

    class Meta:
        app_label = "users"
