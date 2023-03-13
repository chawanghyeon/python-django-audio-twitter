from django.db import models

from babbles.models import Babble
from core.managers import DefaultManager
from users.models import User


class Like(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    babble = models.ForeignKey(Babble, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    objects = DefaultManager()

    def __unicode__(self):
        return self.user.first_name + " likes " + str(self.babble.id)
