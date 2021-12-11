from django.urls import path

from . import views

urlpatterns = [
    path('oktatok/', views.orarendi_oktatok, name='orarendi_oktatok'),
    path('oktatok/<int:oktato_id>/', views.oktato_orarendje, name='oktato_orarendje'),
    path('hallgatok/', views.evfolyamok, name='evfolyamok'),
    path('hallgatok/<int:evfolyam_id>/', views.evfolyam_orarendje, name='evfolyam_orarendje'),
    path('osz/', views.osz, name='osz'),
    path('tavasz/', views.tavasz, name='tavasz'),
]