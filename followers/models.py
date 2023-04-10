from django.db import models

from core.managers import DefaultManager
from users.models import User


class Follower(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, related_name="self", on_delete=models.CASCADE)
    following = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    objects = DefaultManager()

    def __str__(self):
        return self.user.first_name + " follows " + self.following.first_name
