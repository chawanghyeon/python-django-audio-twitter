from django.db import models

from users.models import User


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipient"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
