from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner
        self.auth = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            token = scope["query_string"].decode("utf-8").split("=")[1]
            validated_token = self.auth.get_validated_token(token)
            user = await sync_to_async(self.auth.get_user)(validated_token)
            if user:
                scope["user"] = user

        return await self.inner(scope, receive, send)
