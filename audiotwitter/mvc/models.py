from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    avatar = models.CharField(max_length=140)
    background = models.CharField(max_length=140)
    nickname = models.CharField(max_length=20)
    location = models.CharField(max_length=20)
    phoneNumber = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    bio = models.CharField(max_length=140)
    birthday = models.DateTimeField()

    def __unicode__(self):
        return self.username

class Babble(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fileUrl = models.CharField(max_length=140)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username


class ReBabble(models.Model):
    id = models.IntegerField(primary_key=True)
    babble = models.ForeignKey(Babble)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username


class Comment(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    fileUrl = models.CharField(max_length=140)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username


class Follower(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="follower", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username + " follows " + self.follower.username


class Like(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username + " likes " + self.babble.text


class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    babble = models.ForeignKey(Babble)
    text = models.CharField(max_length=20)
    crated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text
