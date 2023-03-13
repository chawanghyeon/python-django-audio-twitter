from django.db import models

from core.managers import TagManager


class Tag(models.Model):
    text = models.CharField(max_length=20, unique=True, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = TagManager()

    def __unicode__(self):
        return self.text

    def __str__(self):
        return self.text
