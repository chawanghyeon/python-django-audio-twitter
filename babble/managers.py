from typing import Any

from django.contrib.auth.models import UserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class PrivateUserManager(UserManager):
    def get_or_none(self, **kwargs) -> Any | None:
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


class DefaultManager(models.Manager):
    def get_or_none(self, **kwargs) -> Any | None:
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


class TagManager(DefaultManager):
    def get_or_create(self, keyword: str) -> Any:
        try:
            return self.get(text=keyword)
        except ObjectDoesNotExist:
            return self.create(text=keyword)
