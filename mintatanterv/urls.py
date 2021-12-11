from django.urls import path

from . import views

urlpatterns = [
    path('', views.mintatantervek, name='mintatantervek'),
    path('<int:mintatanterv_id>/', views.mintatanterv, name='mintatanterv'),
    path('oszi_kurzusok/', views.oktatok_kurzusai_osz, name='oktatok_kurzusai_osz'),
    path('tavaszi_kurzusok/', views.oktatok_kurzusai_tavasz, name='oktatok_kurzusai_tavasz'),
    path('oszi_kurzusok/<int:oktato_id>/', views.oktato_kurzusai_osz, name='oktato_kurzusai_osz'),
    path('tavaszi_kurzusok/<int:oktato_id>/', views.oktato_kurzusai_tavasz, name='oktato_kurzusai_tavasz'),
    path('oszi_kurzusok/letoltes/', views.xlsx_oktatok_kurzusai_osz, name='xlsx_oktatok_kurzusai_osz'),
    path('tavaszi_kurzusok/letoltes/', views.xlsx_oktatok_kurzusai_tavasz, name='xlsx_oktatok_kurzusai_tavasz'),
    path('kurzusok/<int:kurzus_id>/naplo/', views.kurzus_naplo, name='kurzus_naplo'),
    path('jegyzetfelelosok/', views.jegyzetfelelosok, name='jegyzetfelelosok'),
    path('jegyzetfelelosok/<int:oktato_id>/', views.jegyzetfelelos_targyai, name='jegyzetfelelos_targyai'),
    path('oktatok_elerhetosegei/', views.oktatok_elerhetosegei, name='oktatok_elerhetosegei'),
]