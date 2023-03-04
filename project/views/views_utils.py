from typing import Dict, List

from django.core.cache import caches
from django.db.models import Q

from project.models import Babble, Like, Rebabble, Tag, User
from project.serializers import BabbleSerializer
from project.stt import STT

user_cache = caches["default"]
babble_cache = caches["second"]
stt = STT()


def update_babble_cache(pk: int, field: str, count: int) -> None:
    babble_cache_data = babble_cache.get(pk)
    if babble_cache_data:
        babble_cache_data[field] += count
        babble_cache.set(pk, babble_cache_data)


def update_user_cache(user_pk: int, babble_pk: int, field: str, value: bool) -> None:
    user_cache_data = user_cache.get(user_pk)
    if not user_cache_data:
        return

    babble = user_cache_data.get(babble_pk)
    if babble:
        babble[field] = value
        user_cache.set(user_pk, user_cache_data)


def check_rebabbled(serialized_babbles: List[Dict], user: User) -> List[Dict]:
    rebabbled_babble_pks = set(
        Rebabble.objects.filter(user=user).values_list("babble_pk", flat=True)
    )
    for data in serialized_babbles:
        data["is_rebabbled"] = data["pk"] in rebabbled_babble_pks

    return serialized_babbles


def check_liked(serialized_babbles: List[Dict], user: User) -> List[Dict]:
    liked_babbles_pk = set(
        Like.objects.filter(user=user).values_list("babble_pk", flat=True)
    )
    for data in serialized_babbles:
        data["is_liked"] = data["pk"] in liked_babbles_pk

    return serialized_babbles


def save_keywords(babble: Babble) -> Babble:
    keywords = stt.get_keywords(babble.audio.path)
    tag_objs = Tag.objects.filter(text__in=keywords)
    new_tags = set(keywords) - set(tag_objs.values_list("text", flat=True))

    if new_tags:
        new_tag_objs = [Tag(text=tag) for tag in new_tags]
        Tag.objects.bulk_create(new_tag_objs)
        tag_objs = tag_objs | set(new_tag_objs)

    babble.tags.set(tag_objs)
    babble.save()

    return babble


def set_follower_cache(babble: Babble, user: User) -> None:
    followers = user.following.all()
    babble_pk = babble.pk

    for follower in followers:
        user_pk = follower.user.pk
        user_cache_data = user_cache.get(user_pk, {})
        cache_data = {
            "is_rebabble": False,
            "is_like": False,
        }

        if babble_pk in user_cache_data:
            cache_data.update(user_cache_data[babble_pk])
            user_cache_data.pop(babble_pk)

        user_cache_data[babble_pk] = cache_data

        if len(user_cache_data) > 30:
            user_cache_data.popitem()

        user_cache.set(user_pk, user_cache_data)


def set_user_cache(babble: Babble, user: User) -> None:
    user_cache_data = user_cache.get(user.pk, {})
    user_cache_data[babble.pk] = {
        "is_rebabbled": False,
        "is_liked": False,
    }

    user_cache.set(user.pk, user_cache_data)


def set_caches(babble: Babble, user: User, serialized_data) -> None:
    set_user_cache(babble, user)
    set_follower_cache(babble, user)
    babble_cache.set(babble.pk, serialized_data)


def get_babbles_from_cache(user_cache_data: Dict, user: User) -> List[Dict]:
    cached_babbles = []
    non_cached_babbles = []

    for pk, value in user_cache_data.items():
        babble = babble_cache.get(pk)
        if babble:
            babble.update(value)
            cached_babbles.append(babble)
        else:
            non_cached_babbles.append(pk)

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
        [babble["pk"] for babble in serialized_data]
    )

    for pk in non_exist_babbles:
        user_cache_data.pop(pk, None)
    user_cache.set(user.pk, user_cache_data)


def set_babbles_cache(serialized_data: List[Dict]) -> None:
    for babble in serialized_data:
        babble_cache.set(babble["pk"], babble)


def update_serialized_data(
    serialized_data: List[Dict], user_cache_data: Dict
) -> List[Dict]:
    for babble in serialized_data:
        data = user_cache_data.get(babble["pk"])
        babble.update(data)

    return serialized_data


def get_non_cached_babbles(non_cached_babbles: List[int], user: User) -> List[dict]:
    if not non_cached_babbles:
        return []

    babbles = Babble.objects.filter(pk__in=non_cached_babbles).order_by("-created")
    serializer = BabbleSerializer(babbles, many=True)
    serialized_data = serializer.data

    user_cache_data = user_cache.get(user.pk)

    set_babbles_cache(serialized_data)
    remove_non_existing_babbles(
        non_cached_babbles, serialized_data, user, user_cache_data
    )

    serialized_data = update_serialized_data(serialized_data, user_cache_data)

    return serialized_data


def get_babbles_from_db(user: User) -> List[Babble]:
    babbles = Babble.objects.filter(
        Q(user__in=user.self.all().values_list("following", flat=True)) | Q(user=user)
    ).order_by("-created")[:20]

    serializer = BabbleSerializer(babbles, many=True)
    serialized_babbles = serializer.data

    set_babbles_cache(serialized_babbles)

    serialized_babbles = check_rebabbled(serialized_babbles, user)
    serialized_babbles = check_liked(serialized_babbles, user)

    data = {}
    for babble in serialized_babbles:
        data[babble["pk"]] = {
            "is_rebabbled": babble["is_rebabbled"],
            "is_liked": babble["is_liked"],
        }

    user_cache.set(user.pk, data)

    return serialized_babbles
