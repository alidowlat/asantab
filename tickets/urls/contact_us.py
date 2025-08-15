from django.urls import path
from tickets.views import contact_us

urlpatterns = [
    path('', contact_us, name='contact_us_page'),
]
