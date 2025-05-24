from django.urls import path
from home.views import HomeView, about_us

urlpatterns = [
    path('', HomeView.as_view(), name='index_page'),
    path('about-us/', about_us, name='about_us_page'),
]
