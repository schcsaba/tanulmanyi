from django.urls import path

from . import views

urlpatterns = [
    path('temavezetok/', views.temavezetok, name='temavezetok'),
    path('valaszthatotemavezetok/', views.valaszthato_temavezetok, name='valaszthato_temavezetok'),
    path('aktivtemavezetok/', views.aktiv_temavezetok, name='aktiv_temavezetok'),
    path('megirtesfolyamatban/', views.megirtesfolyamatban_pag_or_search, name='megirtesfolyamatban_pag_or_search'),
    path('megirt/', views.temavezetok_megirt, name='temavezetok_megirt'),
    path('megirtak_jegyenkent/', views.megirtak_jegyenkent, name='megirtak_jegyenkent'),
    path('szakdolgozatrepozitorium/', views.szakdolgozatrepozitorium, name='szakdolgozatrepozitorium'),
    path('kurzusok/', views.kurzusok, name='szakdolgozat_kurzusok'),
]