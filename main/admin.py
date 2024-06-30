from django.contrib import admin

from .models import BlogPost, Chat

admin.site.register(BlogPost)
admin.site.register(Chat)