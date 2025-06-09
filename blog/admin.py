from django.contrib import admin

from blog.models import Post, BlogVisit, Category

admin.site.register(Post)
admin.site.register(BlogVisit)
admin.site.register(Category)
