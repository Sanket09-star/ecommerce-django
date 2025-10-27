"""
URL configuration for greatkart project.

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
from django.contrib import admin
from django.urls import path ,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
   # #admin honeypot for fake login for security reasons to use admin_honeypot need django version 2 or 3 , new version of django 5.2.5 not support admin_honeypot
    path('securelogin/', admin.site.urls), #just rename it to securelogin for security reasons
    path('', views.home, name ='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')), # For Google OAuth
    
    #Orders
    path('orders/', include('orders.urls')),
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
