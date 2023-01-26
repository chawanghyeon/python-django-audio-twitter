from django.contrib import admin

from .models import *

# Register your models here.
admin.register(User)
admin.register(Tag)
admin.register(Babble)
admin.register(Comment)
admin.register(Follower)
admin.register(Like)
