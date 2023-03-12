from typing import Any

from django.contrib.auth.models import UserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404


class PrivateUserManager(UserManager):
    def get_or_404(self, **kwargs) -> Any:
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            raise Http404


class DefaultManager(models.Manager):
    def get_or_404(self, **kwargs) -> Any:
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            raise Http404


class TagManager(DefaultManager):
    def get_or_create(self, text: str) -> Any:
        try:
            return self.get(text=text)
        except ObjectDoesNotExist:
            return self.create(text=text)
