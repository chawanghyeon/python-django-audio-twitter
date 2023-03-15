"""
ASGI config for audiotwitter project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from notifications.consumers import NotificationConsumer
from notifications.middlewares import TokenAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audiotwitter.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": TokenAuthMiddleware(
            URLRouter(
                [
                    path("ws/", NotificationConsumer.as_asgi()),
                ]
            )
        ),
    }
)
