from urllib.parse import urlencode

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.core.paginator import Paginator
from szakdolgozat.models import Temavezeto, TemavezetoTemakor, Tema, HallgatoKepzesTema, ErdemJegy, Beallitas
from tanulmanyi.permissions import oktato_required

# Tema.tema_statusz ids
SZABAD, FOGLALT, MEGIRT, SZABAD_ELKEZDETT, CIMBEJELENTO = 1, 2, 3, 4, 6
NEM_MEGIRT_KIZART = (MEGIRT, 5)

HALLGATOK_PREFETCH = Prefetch(
    'hallgatokepzestema_set',
    queryset=HallgatoKepzesTema.objects.select_related(
        'hallgato_kepzes__hallgato', 'hallgato_kepzes__kepzes__tagozat', 'hallgato_kepzes__statusz', 'erdemjegy'))


def _beallitas_szovege(nev):
    beallitas = Beallitas.objects.filter(nev=nev).first()
    return beallitas.szoveg if beallitas else ''


def _temavezetok_temakorokkel(temavezetok):
    """Loads the visible topic areas, their not-yet-written titles and the students on them,
    plus the per-supervisor counters, in a fixed number of queries."""
    hkt = 'temavezetotemakor__tema__hallgatokepzestema'
    temak = (Tema.objects.exclude(tema_statusz__in=NEM_MEGIRT_KIZART)
             .select_related('tema_statusz').prefetch_related(HALLGATOK_PREFETCH))
    temakorok = (TemavezetoTemakor.objects.filter(rejtett=False).select_related('temakor')
                 .prefetch_related(Prefetch('tema_set', queryset=temak, to_attr='nem_megirt_temak_lista')))
    # Meta.ordering is dropped from GROUP BY queries, so the order is restated here.
    temavezetok = list(temavezetok.order_by('vezeteknev', 'keresztnev').annotate(
        szakd_targyat_felvett=Count(hkt, filter=Q(**{hkt + '__szakdolgozat_targyat_felvett': True}), distinct=True),
        ma_szakdolgozatok_szama=Count(hkt, filter=Q(**{hkt + '__szakdolgozat_targyat_felvett': True,
                                                        hkt + '__hallgato_kepzes__kepzes__kepzes_kod': 'MTN'}),
                                      distinct=True),
        foglalt_helyek=Count('temavezetotemakor__tema', filter=Q(temavezetotemakor__tema__tema_statusz=FOGLALT),
                             distinct=True),
        cimbejelento=Count('temavezetotemakor__tema', filter=Q(temavezetotemakor__tema__tema_statusz=CIMBEJELENTO),
                           distinct=True),
    ).prefetch_related(Prefetch('temavezetotemakor_set', queryset=temakorok, to_attr='valaszthato_temakorok_lista')))

    for temavezeto in temavezetok:
        for temakor in temavezeto.valaszthato_temakorok_lista:
            temak = temakor.nem_megirt_temak_lista
            temakor.szabad_plusz_temak_lista = [t for t in temak if t.tema_statusz_id in (SZABAD, SZABAD_ELKEZDETT)]
            temakor.foglalt_temak_lista = [t for t in temak if t.tema_statusz_id == FOGLALT]
            temakor.szabad_plusz_cimbejelento_temak_lista = [
                t for t in temak if t.tema_statusz_id in (SZABAD, SZABAD_ELKEZDETT, CIMBEJELENTO)]
    return temavezetok


@login_required
def temavezetok(request):
    temavezetok = _temavezetok_temakorokkel(Temavezeto.objects.filter(valaszthato=True))
    for temavezeto in temavezetok:
        temavezeto.szabad_helyek = temavezeto.max_letszam - temavezeto.szakd_targyat_felvett
        temavezeto.szakd_targyat_nem_vett_fel = temavezeto.foglalt_helyek - temavezeto.szakd_targyat_felvett
    args = {}
    args['osszes_szabad_hely'] = sum(t.szabad_helyek for t in temavezetok)
    args['osszes_cimbejelento'] = sum(t.cimbejelento for t in temavezetok)
    args['temavezetok'] = temavezetok
    return render(request, 'szakdolgozat/temavezetok.html', args)


@login_required
def valaszthato_temavezetok(request):
    args = {'temavalasztas_menete': _beallitas_szovege('temavalasztas_menete')}
    return render(request, 'szakdolgozat/valaszthato_temavezetok.html', args)


@login_required
def aktiv_temavezetok(request):
    aktiv_temavezetok = _temavezetok_temakorokkel(Temavezeto.objects.filter(inaktiv=False))
    for temavezeto in aktiv_temavezetok:
        # az MA képzésen írt szakdolgozatok két helyet foglalnak le a témavezető kvótájából,
        # ezért az MA képzésen írt szakdolgozatok számát levonjuk a szabad helyek szamából,
        # így az MA képzésen írt szakdolgozatok kétszer lesznek levonva ebből a számból
        temavezeto.szabad_helyek = (temavezeto.max_letszam - temavezeto.szakd_targyat_felvett
                                    - temavezeto.ma_szakdolgozatok_szama)
    args = {}
    args['osszes_szabad_hely'] = sum(max(t.szabad_helyek, 0) for t in aktiv_temavezetok)
    args['aktiv_temavezetok'] = aktiv_temavezetok
    args['temavalasztas_menete'] = _beallitas_szovege('temavalasztas_menete')
    return render(request, 'szakdolgozat/aktiv_temavezetok.html', args)


def _szakdolgozat_lista(request, hallgatokepzestema, template):
    """Shared search + pagination for the thesis list pages."""
    kereses = {nev: request.GET.get(nev, '') for nev in ('cim', 'hallgato', 'temavezeto')}
    if any(kereses.values()):
        hallgato, temavezeto = kereses['hallgato'], kereses['temavezeto']
        hallgatokepzestema = hallgatokepzestema.filter(
            Q(tema__cim__icontains=kereses['cim']),
            Q(hallgato_kepzes__hallgato__vezeteknev__icontains=hallgato)
            | Q(hallgato_kepzes__hallgato__keresztnev__icontains=hallgato)
            | Q(hallgato_kepzes__hallgato__neptun_kod__icontains=hallgato),
            Q(tema__temavezeto_temakor__temavezeto__vezeteknev__icontains=temavezeto)
            | Q(tema__temavezeto_temakor__temavezeto__keresztnev__icontains=temavezeto)
            | Q(tema__temavezeto_temakor__temavezeto__neptun_kod__icontains=temavezeto))
    hallgatokepzestema = hallgatokepzestema.select_related(
        'hallgato_kepzes__hallgato', 'hallgato_kepzes__kepzes__tagozat', 'tema__tema_statusz',
        'tema__temavezeto_temakor__temavezeto', 'tema__temavezeto_temakor__temakor')

    paginator = Paginator(hallgatokepzestema, 20)
    args = dict(kereses)
    args['kereses_query'] = urlencode(kereses)
    args['paginator'] = paginator
    args['paginatorpage'] = paginator.get_page(request.GET.get('page'))
    return render(request, template, args)


@login_required
def megirtesfolyamatban_pag_or_search(request):
    hallgatokepzestema = (HallgatoKepzesTema.objects.exclude(Q(tema__tema_statusz__exact=FOGLALT), Q(veg__isnull=False))
                          .order_by('-kezdet', '-veg'))
    return _szakdolgozat_lista(request, hallgatokepzestema, 'szakdolgozat/megirtesfolyamatban_pag_or_search.html')


@login_required
def szakdolgozatrepozitorium(request):
    hallgatokepzestema = HallgatoKepzesTema.objects.filter(sikeres_vedes_datuma__isnull=False).order_by('-veg')
    return _szakdolgozat_lista(request, hallgatokepzestema, 'szakdolgozat/szakdolgozatrepozitorium.html')


@oktato_required
def temavezetok_megirt(request):
    temak = Tema.objects.filter(tema_statusz=MEGIRT).select_related('tema_statusz').prefetch_related(HALLGATOK_PREFETCH)
    temakorok = TemavezetoTemakor.objects.select_related('temakor').prefetch_related(
        Prefetch('tema_set', queryset=temak, to_attr='megirt_temak_lista'))
    temavezetok = list(Temavezeto.objects.prefetch_related(
        Prefetch('temavezetotemakor_set', queryset=temakorok, to_attr='temakorok_lista')))
    for temavezeto in temavezetok:
        temavezeto.megirt_temak_db = sum(len(t.megirt_temak_lista) for t in temavezeto.temakorok_lista)
    return render(request, 'szakdolgozat/temavezetok_megirt.html', {'temavezetok': temavezetok})


@oktato_required
def megirtak_jegyenkent(request):
    hallgatokepzestemak = HallgatoKepzesTema.objects.select_related(
        'tema', 'hallgato_kepzes__hallgato', 'hallgato_kepzes__kepzes__tagozat', 'hallgato_kepzes__statusz')
    erdemjegyek = ErdemJegy.objects.prefetch_related(Prefetch('hallgatokepzestema_set', queryset=hallgatokepzestemak))
    return render(request, 'szakdolgozat/megirtak_jegyenkent.html', {'erdemjegyek': erdemjegyek})


@login_required
def kurzusok(request):
    return render(request, 'szakdolgozat/kurzusok.html', {'kurzusok': _beallitas_szovege('kurzusok')})


@login_required
def zarovizsga_tetelek(request):
    return render(request, 'szakdolgozat/zarovizsga_tetelek.html',
                  {'zarovizsga_tetelek': _beallitas_szovege('zarovizsga_tetelek')})
