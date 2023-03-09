from django.contrib import admin

from project.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Babble)
admin.site.register(Comment)
admin.site.register(Follower)
admin.site.register(Like)
admin.site.register(Rebabble)