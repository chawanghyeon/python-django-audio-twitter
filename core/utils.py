import os
import uuid
from typing import Any

from django.utils import timezone


def image_file_path(instance: Any, filename: str) -> str:
    now = timezone.now()
    filepath = now.strftime("image/%Y/%m/%d")
    filename = str(instance.id) + "-" + str(now.strftime("%H%M%S")) + ".jpg"
    return os.path.join(filepath, filename)


def audio_file_path(instance: Any, filename: str) -> str:
    now = timezone.now()
    filepath = now.strftime("audio/%Y/%m/%d")
    filename = str(uuid.uuid4().hex) + "-" + str(now.strftime("%H%M%S")) + ".mp3"
    return os.path.join(filepath, filename)


import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record):
        try:
            log_data = {
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
            }

            temp = None
            try:
                temp = dict(record.msg)
            except ValueError:
                temp = None

            if isinstance(temp, dict):
                for key, value in temp.items():
                    log_data[key] = value
                del log_data["message"]
        except Exception as e:
            print(e)
            log_data = {
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
            }

        return json.dumps(log_data, ensure_ascii=False).encode("utf-8")
