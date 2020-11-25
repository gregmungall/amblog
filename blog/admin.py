from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from . import models


# Admin comment list modifications
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'created_date')
    search_fields = ['text', 'author__username', 'post__title']
    list_filter = ['author__username', 'post__title']


# Admin post list modifications
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'publish_date')
    search_fields = ['title', 'author__username']
    list_filter = ['author__username', 'tags__name']


# Admin tag list modifications
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']


# Model registration
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Comment, CommentAdmin)


# Admin general page modifications
AdminSite.site_header = "Alison Mungall's blog admin"
AdminSite.site_title = "Alison's blog admin"
