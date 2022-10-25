from django.contrib import admin
from .models import FollowUser, PostLike, Profile, Post
# Register your models here.

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(PostLike)
admin.site.register(FollowUser)