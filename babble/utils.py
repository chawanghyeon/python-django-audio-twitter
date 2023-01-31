import datetime
import os
from typing import Any

from django.utils import timezone


def image_file_path(instance: Any, filename: str) -> str:
    ext: str = filename.split(".")[-1]
    now: datetime = timezone.now()
    filepath: Any = now.strftime("image/%Y/%m/%d")
    filename: str = str(instance.id) + str(now.strftime("%H%M%S")) + "." + ext
    return os.path.join(filepath, filename)
