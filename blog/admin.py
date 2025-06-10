from django.contrib import admin

from blog.models import Post, BlogVisit, Category, PostTag

admin.site.register(Post)
admin.site.register(BlogVisit)
admin.site.register(PostTag)
admin.site.register(Category)
