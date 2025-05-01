from django.urls import path
from home import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index_page'),
    path('about-us/', views.about_us, name='about_us_page'),
]
