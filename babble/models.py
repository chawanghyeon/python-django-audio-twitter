from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.IntegerField(primary_key=True, unique=True, blank=True)
    birthday = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to="image/%Y/%m/%d", blank=True, null=True)
    background = models.ImageField(upload_to="image/%Y/%m/%d", blank=True, null=True)
    nickname = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=20, blank=True)
    number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    bio = models.CharField(max_length=140, blank=True)

    def __unicode__(self):
        return self.first_name

    def __str__(self):
        return "%d %s" % (self.first_name, self.image)


class Tag(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, blank=True)
    text = models.CharField(max_length=20)
    crated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text


class Babble(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reBabble = models.ForeignKey("self", on_delete=models.CASCADE, blank=True)
    audio = models.FileField(upload_to="audio/%Y/%m/%d", blank=True)
    duration = models.IntegerField(blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __unicode__(self):
        return self.user.first_name


class Comment(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    audio = models.FileField(upload_to="audio/%Y/%m/%d")
    duration = models.IntegerField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, blank=True)

    def __unicode__(self):
        return self.user.first_name


class Follower(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.first_name + " follows " + self.following.first_name


class Like(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.first_name + " likes " + str(self.babble.id)
