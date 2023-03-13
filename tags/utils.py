from typing import Dict, List

from likes.models import Like
from rebabbles.models import Rebabble
from users.models import User


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
