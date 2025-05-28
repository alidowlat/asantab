"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django.conf.urls
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import home.views
from main import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('', include('config.urls.actions')),
    path('auth/', include('accounts.urls')),
    path('services/', include('services.urls.list')),
    path('services/', include('services.urls.detail')),
    path('profile/', include('dashboard.urls.profile')),
    path('profile/', include('dashboard.urls.favorite')),
    path('profile/', include('dashboard.urls.visit')),
    path('profile/', include('dashboard.urls.account')),
    path('profile/', include('dashboard.urls.change_number')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

django.conf.urls.handler404 = home.views.error_404

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]