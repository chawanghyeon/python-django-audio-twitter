from typing import Dict, List, Optional

from django.core.cache import caches
from django.db.models import Q
from django.http import HttpRequest

from project.models import Babble, Follower, Like, Rebabble, Tag, User
from project.serializers import BabbleSerializer
from project.stt import STT

user_cache = caches["default"]
babble_cache = caches["second"]
stt = STT()


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


def save_keywords(babble: Babble) -> Babble:
    keywords = stt.get_keywords(babble.audio.path)
    tag_objs = Tag.objects.filter(text__in=keywords)
    new_tags = set(keywords) - set(tag_objs.values_list("text", flat=True))

    if new_tags:
        new_tag_objs = [Tag(text=tag) for tag in new_tags]
        new_tag_objs = Tag.objects.bulk_create(new_tag_objs)
        tag_objs = set(tag_objs) | set(new_tag_objs)

    babble.tags.set(tag_objs)
    babble.save()

    return babble


def set_follower_cache(babble: Babble, user: User) -> None:
    followers = user.following.all()
    babble_id = babble.id

    for follower in followers:
        user_id = follower.user.id
        user_cache_data = user_cache.get(user_id, {})
        cache_data = {
            "is_rebabble": False,
            "is_like": False,
        }

        if babble_id in user_cache_data:
            cache_data.update(user_cache_data[babble_id])
            user_cache_data.pop(babble_id)

        user_cache_data[babble_id] = cache_data

        if len(user_cache_data) > 30:
            user_cache_data.popitem()

        user_cache.set(user_id, user_cache_data)


def set_user_cache(babble: Babble, user: User) -> None:
    user_cache_data = user_cache.get(user.id, {})
    user_cache_data[babble.id] = {
        "is_rebabbled": False,
        "is_liked": False,
    }

    user_cache.set(user.id, user_cache_data)


def set_caches(babble: Babble, user: User, serialized_data) -> None:
    set_user_cache(babble, user)
    set_follower_cache(babble, user)
    babble_cache.set(babble.id, serialized_data)


def get_babbles_from_cache(user_cache_data: Dict, user: User, next: int) -> List[Dict]:
    cached_babbles = []
    non_cached_babbles = []

    start = next if next else 0
    user_cache_data = dict(list(user_cache_data.items())[start : start + 5])

    for id, value in user_cache_data.items():
        babble = babble_cache.get(id)
        if babble:
            babble.update(value)
            cached_babbles.append(babble)
        else:
            non_cached_babbles.append(id)

    non_cached_babbles = get_non_cached_babbles(non_cached_babbles, user)
    babbles = cached_babbles + non_cached_babbles
    return sorted(babbles, key=lambda x: x["created"], reverse=True)


def remove_non_existing_babbles(
    non_cached_babbles: List,
    serialized_data: List[Dict],
    user: User,
    user_cache_data: Dict,
) -> None:
    non_exist_babbles = set(non_cached_babbles) - set(
        [babble["id"] for babble in serialized_data]
    )

    for id in non_exist_babbles:
        user_cache_data.pop(id, None)
    user_cache.set(user.id, user_cache_data)


def set_babbles_cache(serialized_data: List[Dict]) -> None:
    for babble in serialized_data:
        babble_cache.set(babble["id"], babble)


def update_serialized_data(
    serialized_data: List[Dict], user_cache_data: Dict
) -> List[Dict]:
    for babble in serialized_data:
        data = user_cache_data.get(babble["id"])
        babble.update(data)

    return serialized_data


def get_non_cached_babbles(non_cached_babbles: List[int], user: User) -> List[dict]:
    if not non_cached_babbles:
        return []

    babbles = Babble.objects.filter(id__in=non_cached_babbles).order_by("-created")
    serializer = BabbleSerializer(babbles, many=True)
    serialized_data = serializer.data

    user_cache_data = user_cache.get(user.id)

    set_babbles_cache(serialized_data)
    remove_non_existing_babbles(
        non_cached_babbles, serialized_data, user, user_cache_data
    )

    serialized_data = update_serialized_data(serialized_data, user_cache_data)

    return serialized_data


def get_babbles_from_db(user: User, next: int) -> List[Babble]:
    start = 0
    end = 20

    if next >= 20:
        start = next
        end = start + 5

    babbles = Babble.objects.filter(
        Q(user__in=user.self.all().values_list("following", flat=True)) | Q(user=user)
    ).order_by("-created")[start:end]

    serializer = BabbleSerializer(babbles, many=True)
    serialized_data = serializer.data

    set_babbles_cache(serialized_data)

    serialized_data = check_rebabbled(serialized_data, user)
    serialized_data = check_liked(serialized_data, user)

    data = {}
    for babble in serialized_data:
        data[babble["id"]] = {
            "is_rebabbled": babble["is_rebabbled"],
            "is_liked": babble["is_liked"],
        }

    user_cache.set(user.id, data)

    return serialized_data[0:5]


def get_user(request: HttpRequest, pk: Optional[str] = None) -> User:
    id = request.query_params.get("user", None)

    if id is None and pk is not None:
        id = pk

    if id is None:
        user = request.user
    else:
        user = User.objects.get(id=id)

    return user


def check_is_following(user: User, follower: User, serialized_data: Dict) -> Dict:
    if user == follower:
        return serialized_data

    if Follower.objects.filter(user=user, following=follower).exists():
        serialized_data["is_following"] = True
    else:
        serialized_data["is_following"] = False

    return serialized_data
