from django.urls import path

from . import views

urlpatterns = [
    path('', views.szabalyzatok, name='szabalyzatok'),
    path('letoltes/<int:szabalyzat_id>/', views.szabalyzat_letoltes, name='szabalyzat_letoltes'),
]