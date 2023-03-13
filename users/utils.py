from typing import Dict, Optional

from django.http import HttpRequest

from followers.models import Follower
from users.models import User


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


def check_is_following(user: User, follower: User, serialized_data: Dict) -> Dict:
    if user == follower:
        return serialized_data

    if Follower.objects.filter(user=user, following=follower).exists():
        serialized_data["is_following"] = True
    else:
        serialized_data["is_following"] = False

    return serialized_data
