from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from szakdolgozat.models import Temavezeto, Tema, HallgatoKepzesTema, ErdemJegy, Beallitas


@login_required
def temavezetok(request):
    temavezetok = Temavezeto.objects.filter(valaszthato=True)
    osszes_szabad_hely = 0
    osszes_cimbejelento = 0
    for temavezeto in temavezetok:
        temavezeto.szakd_targyat_felvett = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto__exact=temavezeto.id).filter(szakdolgozat_targyat_felvett__exact=1).count()
        # temavezeto.kerveny = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto__exact=temavezeto.id).filter(kerveny__in=['kerveny_01', 'kerveny_02']).count()
        # temavezeto.szabad_helyek = temavezeto.max_letszam - temavezeto.szakd_targyat_felvett - temavezeto.kerveny
        temavezeto.szabad_helyek = temavezeto.max_letszam - temavezeto.szakd_targyat_felvett
        temavezeto.foglalt_helyek = Tema.foglalt.filter(temavezeto_temakor__temavezeto__exact=temavezeto.id).count()
        temavezeto.szakd_targyat_nem_vett_fel = temavezeto.foglalt_helyek - temavezeto.szakd_targyat_felvett
        temavezeto.cimbejelento = Tema.cimbejelento.filter(temavezeto_temakor__temavezeto__exact=temavezeto.id).count()
        osszes_szabad_hely = osszes_szabad_hely + temavezeto.szabad_helyek
        osszes_cimbejelento = osszes_cimbejelento + temavezeto.cimbejelento
    args = {}
    args['osszes_szabad_hely'] = osszes_szabad_hely
    args['osszes_cimbejelento'] = osszes_cimbejelento
    args['temavezetok'] = temavezetok
    return render(request, 'szakdolgozat/temavezetok.html', args)


@login_required
def valaszthato_temavezetok(request):
    valaszthato_temavezetok = Temavezeto.objects.filter(valaszthato=True)
    osszes_szabad_hely = 0
    #osszes_cimbejelento = 0
    for temavezeto in valaszthato_temavezetok:
        temavezeto.szakd_targyat_felvett = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto__exact=temavezeto.id).filter(szakdolgozat_targyat_felvett__exact=1).count()
        # temavezeto.kerveny = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto__exact=temavezeto.id).filter(kerveny__in=['kerveny_01', 'kerveny_02']).count()
        # temavezeto.szabad_helyek = temavezeto.max_letszam - temavezeto.szakd_targyat_felvett - temavezeto.kerveny
        temavezeto.szabad_helyek = temavezeto.max_letszam - temavezeto.szakd_targyat_felvett
        #temavezeto.foglalt_helyek = Tema.foglalt.filter(temavezeto_temakor__temavezeto__exact=temavezeto.id).count()
        #temavezeto.szakd_targyat_nem_vett_fel = temavezeto.foglalt_helyek - temavezeto.szakd_targyat_felvett
        #temavezeto.cimbejelento = Tema.cimbejelento.filter(temavezeto_temakor__temavezeto__exact=temavezeto.id).count()
        osszes_szabad_hely = osszes_szabad_hely + temavezeto.szabad_helyek
        #osszes_cimbejelento = osszes_cimbejelento + temavezeto.cimbejelento
    args = {}
    args['osszes_szabad_hely'] = osszes_szabad_hely
    #args['osszes_cimbejelento'] = osszes_cimbejelento
    args['valaszthato_temavezetok'] = valaszthato_temavezetok
    if Beallitas.objects.get(nev='temavalasztas_menete'):
        temavalasztas_menete = Beallitas.objects.get(nev='temavalasztas_menete')
        args['temavalasztas_menete'] = temavalasztas_menete.szoveg
    else:
        args['temavalasztas_menete'] = ''
    return render(request, 'szakdolgozat/valaszthato_temavezetok.html', args)


@login_required
def aktiv_temavezetok(request):
    aktiv_temavezetok = Temavezeto.objects.filter(inaktiv=False)
    osszes_szabad_hely = 0
    #osszes_cimbejelento = 0
    for temavezeto in aktiv_temavezetok:
        temavezeto.szakd_targyat_felvett = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto__exact=temavezeto.id).filter(szakdolgozat_targyat_felvett__exact=1).count()
        # temavezeto.kerveny = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto__exact=temavezeto.id).filter(kerveny__in=['kerveny_01', 'kerveny_02']).count()
        # temavezeto.szabad_helyek = temavezeto.max_letszam - temavezeto.szakd_targyat_felvett - temavezeto.kerveny
        temavezeto.szabad_helyek = temavezeto.max_letszam - temavezeto.szakd_targyat_felvett
        temavezeto.foglalt_helyek = Tema.foglalt.filter(temavezeto_temakor__temavezeto__exact=temavezeto.id).count()
        #temavezeto.szakd_targyat_nem_vett_fel = temavezeto.foglalt_helyek - temavezeto.szakd_targyat_felvett
        #temavezeto.cimbejelento = Tema.cimbejelento.filter(temavezeto_temakor__temavezeto__exact=temavezeto.id).count()
        osszes_szabad_hely = osszes_szabad_hely + temavezeto.szabad_helyek
        #osszes_cimbejelento = osszes_cimbejelento + temavezeto.cimbejelento
    args = {}
    args['osszes_szabad_hely'] = osszes_szabad_hely
    #args['osszes_cimbejelento'] = osszes_cimbejelento
    args['aktiv_temavezetok'] = aktiv_temavezetok
    if Beallitas.objects.get(nev='temavalasztas_menete'):
        temavalasztas_menete = Beallitas.objects.get(nev='temavalasztas_menete')
        args['temavalasztas_menete'] = temavalasztas_menete.szoveg
    else:
        args['temavalasztas_menete'] = ''
    return render(request, 'szakdolgozat/aktiv_temavezetok.html', args)


@login_required
def megirtesfolyamatban_pag_or_search(request):
    args = {}
    if request.GET.get('cim') or request.GET.get('hallgato') or request.GET.get('temavezeto'):
        cim = request.GET.get('cim')
        args['cim'] = cim
        hallgato = request.GET.get('hallgato')
        args['hallgato'] = hallgato
        temavezeto = request.GET.get('temavezeto')
        args['temavezeto'] = temavezeto
        hallgatokepzestema = HallgatoKepzesTema.objects.filter(tema__cim__icontains=cim).filter(Q(hallgato_kepzes__hallgato__vezeteknev__icontains=hallgato) | Q(hallgato_kepzes__hallgato__keresztnev__icontains=hallgato) | Q(hallgato_kepzes__hallgato__neptun_kod__icontains=hallgato)).filter(Q(tema__temavezeto_temakor__temavezeto__vezeteknev__icontains=temavezeto) | Q(tema__temavezeto_temakor__temavezeto__keresztnev__icontains=temavezeto) | Q(tema__temavezeto_temakor__temavezeto__neptun_kod__icontains=temavezeto)).exclude(tema__tema_statusz__exact=4).order_by('-kezdet', '-veg')
    else:
        hallgatokepzestema = HallgatoKepzesTema.objects.exclude(tema__tema_statusz__exact=4).order_by('-kezdet', '-veg')

    paginator = Paginator(hallgatokepzestema, 20)
    args['paginator'] = paginator
    page = request.GET.get('page')

    try:
        args['paginatorpage'] = paginator.page(page)
    except PageNotAnInteger:
        args['paginatorpage'] = paginator.page(1)
    except EmptyPage:
        args['paginatorpage'] = paginator.page(paginator.num_pages)

    return render(request, 'szakdolgozat/megirtesfolyamatban_pag_or_search.html', args)


@login_required
def szakdolgozatrepozitorium(request):
    args = {}
    if request.GET.get('cim') or request.GET.get('hallgato') or request.GET.get('temavezeto'):
        cim = request.GET.get('cim')
        args['cim'] = cim
        hallgato = request.GET.get('hallgato')
        args['hallgato'] = hallgato
        temavezeto = request.GET.get('temavezeto')
        args['temavezeto'] = temavezeto
        hallgatokepzestema = HallgatoKepzesTema.objects.filter(tema__cim__icontains=cim).filter(Q(hallgato_kepzes__hallgato__vezeteknev__icontains=hallgato) | Q(hallgato_kepzes__hallgato__keresztnev__icontains=hallgato) | Q(hallgato_kepzes__hallgato__neptun_kod__icontains=hallgato)).filter(Q(tema__temavezeto_temakor__temavezeto__vezeteknev__icontains=temavezeto) | Q(tema__temavezeto_temakor__temavezeto__keresztnev__icontains=temavezeto) | Q(tema__temavezeto_temakor__temavezeto__neptun_kod__icontains=temavezeto)).filter(tema__tema_statusz__exact=3).filter(veg__year__gte=2013).filter(erdemjegy__isnull=False).filter(hallgato_kepzes__statusz__in=[2, 4, 5, 9]).order_by('-veg')
    else:
        hallgatokepzestema = HallgatoKepzesTema.objects.filter(tema__tema_statusz__exact=3).filter(veg__year__gte=2013).filter(erdemjegy__isnull=False).filter(hallgato_kepzes__statusz__in=[2, 4, 5, 9]).order_by('-veg')

    paginator = Paginator(hallgatokepzestema, 20)
    args['paginator'] = paginator
    page = request.GET.get('page')

    try:
        args['paginatorpage'] = paginator.page(page)
    except PageNotAnInteger:
        args['paginatorpage'] = paginator.page(1)
    except EmptyPage:
        args['paginatorpage'] = paginator.page(paginator.num_pages)

    return render(request, 'szakdolgozat/szakdolgozatrepozitorium.html', args)


def in_oktatok_group(user):
    return user.is_authenticated and user.groups.filter(name='Oktatok').exists()

@user_passes_test(in_oktatok_group)
def temavezetok_megirt(request):
    args = {}
    args['temavezetok'] = Temavezeto.objects.all()
    return render(request, 'szakdolgozat/temavezetok_megirt.html', args)


@user_passes_test(in_oktatok_group)
def megirtak_jegyenkent(request):
    args = {}
    args['erdemjegyek'] = ErdemJegy.objects.all()
    return render(request, 'szakdolgozat/megirtak_jegyenkent.html', args)
