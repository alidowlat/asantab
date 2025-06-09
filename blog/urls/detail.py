from django.urls import path
from blog.views import BlogDetailView

urlpatterns = [
    path('<slug:slug>/', BlogDetailView.as_view(), name='post_detail'),
]
