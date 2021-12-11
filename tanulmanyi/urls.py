"""tanulmanyi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import include, path
from django.contrib.admin import AdminSite

from . import views

AdminSite.enable_nav_sidebar = False
AdminSite.site_header = 'BHF Tanulmányi Osztály'
AdminSite.site_title = 'BHF TO'
AdminSite.index_title = 'Adatok karbantartása'

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/auth/', views.auth_view, name='auth_view'),
    path('accounts/loggedin/', views.loggedin, name='loggedin'),
    path('accounts/invalid/', views.invalid_login, name='invalid_login'),
    path('accounts/logout/', views.logout, name='logout'),
    path('szabalyzatok/', include('szabalyzat.urls')),
    path('szakdolgozatok/', include('szakdolgozat.urls')),
    path('mintatantervek/', include('mintatanterv.urls')),
    path('orarendek/', include('orarend.urls')),
    path('faq/', include('faq.urls')),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
]
