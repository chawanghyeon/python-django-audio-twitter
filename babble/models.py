from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)
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
    babble = models.ForeignKey(Babble, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fileUrl = models.CharField(max_length=140)
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
    following = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username + " follows " + self.following.username


class Like(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username + " likes " + self.babble.text


class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    text = models.CharField(max_length=20)
    crated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text
