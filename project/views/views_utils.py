from typing import Dict, List

from django.core.cache import caches
from django.db.models import Q

from project.models import Babble, Like, Rebabble, Tag, User
from project.serializers import BabbleSerializer
from project.stt import STT

user_cache = caches["default"]
babble_cache = caches["second"]
stt = STT()


def check_rebabbled(serialized_babbles: Dict, user: User) -> Dict:
    rebabbled_babble_ids = set(
        Rebabble.objects.filter(user=user).values_list("babble_id", flat=True)
    )
    for data in serialized_babbles:
        data["is_rebabbled"] = data["id"] in rebabbled_babble_ids

    return serialized_babbles


def check_liked(serialized_babbles: Dict, user: User) -> Dict:
    liked_babbles_id = set(
        Like.objects.filter(user=user).values_list("babble_id", flat=True)
    )
    for data in serialized_babbles:
        data["is_liked"] = data["id"] in liked_babbles_id

    return serialized_babbles


def save_keywords(babble: Babble) -> Babble:
    babble.tags.clear()
    keywords = stt.get_keywords(babble.audio.path)
    tags = []

    for keyword in keywords:
        tag = Tag.objects.get_or_create(text=keyword)
        tags.append(tag)

    babble.tags.add(*tags)
    babble.save()

    return babble


def set_follower_cache(babble: Babble, user: User) -> None:
    followers = user.following.all()

    data_for_cache = {
        "id": babble.id,
        "is_rebabble": False,
        "is_like": False,
    }

    for follower in followers:
        user_cache_data = user_cache.get(follower.id) or []

        for data in user_cache_data:
            if data["id"] == babble.id:
                if data["is_rebabble"]:
                    data_for_cache["is_rebabble"] = True
                if data["is_like"]:
                    data_for_cache["is_like"] = True

                user_cache_data.remove(data)
                break

        user_cache_data.append(data_for_cache)

        if len(user_cache_data) > 20:
            user_cache_data.popitem(last=False)

        user_cache.set(follower.id, user_cache_data, 60 * 60 * 24 * 7)


def get_babbles_from_cache(user_cache_data: List[Dict], user: User) -> List[Babble]:
    cached_babbles = []
    non_cached_babbles = []

    for cached_babble in user_cache_data:
        babble = babble_cache.get(cached_babble["id"])
        if babble:
            if cached_babble["is_rebabbled"]:
                babble["is_rebabbled"] = True
            if cached_babble["is_liked"]:
                babble["is_liked"] = True
            cached_babbles.append(babble)
        else:
            non_cached_babbles.append(cached_babble["id"])

    non_cached_babbles, non_exist_babbles = get_non_cached_babbles(
        non_cached_babbles, user
    )

    for non_exist_babble in non_exist_babbles:
        for cached_babble in user_cache_data:
            if non_exist_babble == cached_babble["id"]:
                user_cache_data.remove(cached_babble)
                break

    user_cache.set(user.id, user_cache_data, 60 * 60 * 24 * 7)

    result = cached_babbles + non_cached_babbles
    result.sort(key=lambda x: x["created"], reverse=True)
    return result


def get_non_cached_babbles(
    non_cached_babbles: List[int], user_cache_data: List[Dict]
) -> List[dict]:
    if not non_cached_babbles:
        return []

    babbles = Babble.objects.filter(id__in=non_cached_babbles).order_by("-created")
    serializer = BabbleSerializer(babbles, many=True)

    non_cached_babbles = set(non_cached_babbles)
    exist_babbles = set()

    for babble in serializer.data:
        if babble.id in non_cached_babbles:
            exist_babbles.add(babble.id)

    non_exist_babbles = list(non_cached_babbles - exist_babbles)

    non_cached_babbles = serializer.data

    for babble in serializer.data:
        babble_cache.set(babble["id"], babble, 60 * 60 * 24 * 7)

    for babble in non_cached_babbles:
        for cached_babble in user_cache_data:
            if babble["id"] == cached_babble["id"]:
                if cached_babble["is_rebabbled"]:
                    babble["is_rebabbled"] = True
                if cached_babble["is_liked"]:
                    babble["is_liked"] = True
                break

    return non_cached_babbles, non_exist_babbles


def get_babbles_from_db(user: User) -> List[Babble]:
    babbles = Babble.objects.filter(
        Q(user__in=user.self.all().values_list("following", flat=True)) | Q(user=user)
    ).order_by("-created")[:20]

    serializer = BabbleSerializer(babbles, many=True)

    for babble in serializer.data:
        babble_cache.set(babble["id"], babble, 60 * 60 * 24 * 7)

    serialized_babbles = serializer.data

    serialized_babbles = check_rebabbled(serialized_babbles, user)
    serialized_babbles = check_liked(serialized_babbles, user)

    data = []
    for babble in serialized_babbles:
        data.append(
            {
                "id": babble["id"],
                "is_rebabbled": babble["is_rebabbled"],
                "is_liked": babble["is_liked"],
            }
        )

    user_cache.set(user.id, data, 60 * 60 * 24 * 7)

    return serialized_babbles
