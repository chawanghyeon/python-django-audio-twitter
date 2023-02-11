from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import *
from .utils import *


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
    objects = PrivateUserManager()

    def __unicode__(self):
        return self.first_name

    def __str__(self):
        return self.first_name


class Tag(models.Model):
    text = models.CharField(max_length=20, unique=True, primary_key=True)
    crated = models.DateTimeField(auto_now_add=True)
    objects = TagManager()

    def __unicode__(self):
        return self.text

    def __str__(self):
        return self.text


class Babble(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rebabble = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    audio = models.FileField(upload_to=audio_file_path, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    like_count = models.IntegerField(default=0, blank=True, null=True)
    comment_count = models.IntegerField(default=0, blank=True, null=True)
    rebabble_count = models.IntegerField(default=0, blank=True, null=True)
    objects = DefaultManager()

    def __unicode__(self):
        return self.user.first_name


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


class Follower(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    objects = DefaultManager()

    def __unicode__(self):
        return self.user.first_name + " follows " + self.following.first_name


class Like(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    objects = DefaultManager()

    def __unicode__(self):
        return self.user.first_name + " likes " + str(self.babble.id)
