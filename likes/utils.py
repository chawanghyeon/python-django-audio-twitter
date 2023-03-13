from typing import Dict, List, Optional

from django.core.cache import caches
from django.http import HttpRequest

from likes.models import Like
from rebabbles.models import Rebabble
from users.models import User

user_cache = caches["default"]
babble_cache = caches["second"]


def update_babble_cache(id: int, field: str, count: int) -> None:
    babble_cache_data = babble_cache.get(id)
    if babble_cache_data:
        babble_cache_data[field] += count
        babble_cache.set(id, babble_cache_data)


def update_user_cache(user_id: int, babble_id: int, field: str, value: bool) -> None:
    user_cache_data = user_cache.get(user_id)
    if not user_cache_data:
        return

    babble = user_cache_data.get(babble_id)
    if babble:
        babble[field] = value
        user_cache.set(user_id, user_cache_data)


def check_rebabbled(serialized_babbles: List[Dict], user: User) -> List[Dict]:
    rebabbled_babble_ids = set(
        Rebabble.objects.filter(user=user).values_list("babble_id", flat=True)
    )
    for data in serialized_babbles:
        data["is_rebabbled"] = data["id"] in rebabbled_babble_ids

    return serialized_babbles


def check_liked(serialized_babbles: List[Dict], user: User) -> List[Dict]:
    liked_babbles_id = set(
        Like.objects.filter(user=user).values_list("babble_id", flat=True)
    )
    for data in serialized_babbles:
        data["is_liked"] = data["id"] in liked_babbles_id

    return serialized_babbles


def get_user(request: HttpRequest, pk: Optional[str] = None) -> User:
    id = request.query_params.get("user", None)

    if id is None and pk is not None:
        id = pk

    if id is None:
        user = request.user
    else:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            raise User.DoesNotExist

    return user
