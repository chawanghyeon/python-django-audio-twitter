import datetime
import os
import uuid
from typing import Any

from django.utils import timezone


def image_file_path(instance: Any, filename: str) -> str:
    now: datetime = timezone.now()
    filepath: Any = now.strftime("image/%Y/%m/%d")
    filename: str = str(instance.id) + "-" + str(now.strftime("%H%M%S")) + ".jpg"
    return os.path.join(filepath, filename)


def audio_file_path(instance: Any, filename: str) -> str:
    now: datetime = timezone.now()
    filepath: Any = now.strftime("audio/%Y/%m/%d")
    filename: str = str(uuid.uuid4().hex) + "-" + str(now.strftime("%H%M%S")) + ".mp3"
    return os.path.join(filepath, filename)
