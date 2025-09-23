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
    path('wallet/', include('wallet.urls.wallet')),
    path('wallet/', include('wallet.urls.transactions')),
    path('wallet/', include('wallet.urls.deposit')),
    path('wallet/', include('wallet.urls.withdrawal')),
    path('auth/user/', include('accounts.urls.user')),
    path('auth/provider/', include('accounts.urls.provider')),
    path('services/', include('services.urls.list')),
    path('services/', include('services.urls.detail')),
    path('blog/', include('blog.urls.list')),
    path('blog/', include('blog.urls.detail')),
    path('profile/', include('dashboard.urls.profile')),
    path('profile/', include('dashboard.urls.favorite')),
    path('profile/', include('dashboard.urls.visit')),
    path('profile/', include('dashboard.urls.account')),
    path('profile/', include('dashboard.urls.change_number')),
    path('profile/', include('dashboard.urls.notification')),
    path('profile/', include('dashboard.urls.order')),
    path('profile/', include('dashboard.urls.service')),
    path('profile/', include('dashboard.urls.roles')),
    path('profile/', include('dashboard.urls.bank_account')),
    path('profile/', include('dashboard.urls.withdrawal')),
    path('', include('search.urls')),
    path('orders/', include('orders.urls.cart')),
    path('contact-us/', include('tickets.urls.contact_us')),
]

django.conf.urls.handler404 = home.views.error_404

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]