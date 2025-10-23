from django.urls import path
from home.views import HomeView, about_us, error_404, FAQ, rules

urlpatterns = [
    path('', HomeView.as_view(), name='index_page'),
    path('about-us/', about_us, name='about_us_page'),
    path('faq/', FAQ, name='faq_page'),
    path('rules/', rules, name='rules_page'),
    path('not-found/', error_404, name='error_404'),
]
