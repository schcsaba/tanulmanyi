import os
from functools import lru_cache

from bs4 import BeautifulSoup
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orarend.models import Beallitas, OrarendFajl

NEM_ERHETO_EL = {'visszajelzes': 'Az órarend még nem érhető el.', 'title': 'Türelmét kérjük!'}


@lru_cache(maxsize=64)
def _feldolgoz(path, mtime, oktatoi):
    """Parses an exported timetable file once per version (mtime is part of the cache key).

    Returns the names listed on it, each name's timetable table cleaned up for display,
    and the notes following the first table (only used for year-group files)."""
    with open(path) as f:
        soup = BeautifulSoup(f, 'html.parser')
    megjegyzesek = None if oktatoi else soup.table.next_sibling.next_sibling.prettify()
    elemek = soup.find_all('li')
    nevek = [elem.string if oktatoi else elem.a.string for elem in elemek]
    tablak = []
    for elem in elemek:
        link = elem.find('a', href=True)
        orarend = soup.find(id=link['href'][1:]) if link else None
        if orarend is None:
            tablak.append(None)
            continue
        [x.extract() for x in orarend('caption')]
        [x.extract() for x in orarend('div', {'class': 'studentsset'})]
        orarend.th.extract()  # Eltávolítja az oktató/évfolyam nevét.
        orarend.td['rowspan'] = '1'
        orarend.th.insert_before(soup.new_tag('th'))
        orarend.tr.extract()
        tablak.append(orarend.prettify())
    return nevek, tablak, megjegyzesek


def _feldolgozott(fajl, oktatoi):
    path = fajl.orarendfajl.path
    return _feldolgoz(path, os.path.getmtime(path), oktatoi)


def _aktiv_fajlok(oktatoi):
    return OrarendFajl.objects.filter(aktiv=True, oktatoi_orarendfajl=oktatoi)


def _nevsor(request, oktatoi, template, kulcs):
    elso_fajl = _aktiv_fajlok(oktatoi).order_by('pk').first()
    if elso_fajl is None:
        return render(request, template, dict(NEM_ERHETO_EL))
    nevek, _, _ = _feldolgozott(elso_fajl, oktatoi)
    return render(request, template, {kulcs: nevek})


def _orarend(request, oktatoi, index, template, nev_kulcs):
    fajlok = list(_aktiv_fajlok(oktatoi).order_by('orarendfajl'))
    szunet = Beallitas.objects.filter(nev='Szünet').first()
    if not fajlok or szunet is None:
        return render(request, template, dict(NEM_ERHETO_EL))

    hetek = [_feldolgozott(fajl, oktatoi) for fajl in fajlok]
    try:
        args = {nev_kulcs: hetek[-1][0][index], 'orarendek': [tablak[index] for _, tablak, _ in hetek]}
    except IndexError:
        raise Http404
    if None in args['orarendek']:
        raise Http404
    try:
        args['szunet'] = int(szunet.ertek)
    except ValueError:
        args['szunet'] = 0
    if not oktatoi:
        args['megjegyzesek'] = _feldolgozott(_aktiv_fajlok(oktatoi).order_by('pk').first(), oktatoi)[2]
    return render(request, template, args)


@login_required
def orarendi_oktatok(request):
    return _nevsor(request, True, 'orarend/orarendi_oktatok.html', 'oktato_nevek')


@login_required
def oktato_orarendje(request, oktato_id):
    return _orarend(request, True, oktato_id, 'orarend/oktato_orarendje.html', 'oktato_neve')


@login_required
def evfolyamok(request):
    return _nevsor(request, False, 'orarend/evfolyamok.html', 'evfolyam_nevek')


@login_required
def evfolyam_orarendje(request, evfolyam_id):
    return _orarend(request, False, evfolyam_id, 'orarend/evfolyam_orarendje.html', 'evfolyam_neve')


def _naptar(request, nev, cim):
    beallitas = Beallitas.objects.filter(nev=nev).first()
    if beallitas:
        args = {'naptar': beallitas.ertek, 'title': cim}
    else:
        args = {'visszajelzes': 'Az oktatási naptár még nem érhető el.', 'title': 'Türelmét kérjük!'}
    args['cim'] = cim
    return render(request, 'orarend/naptar.html', args)


@login_required
def tavasz(request):
    return _naptar(request, 'Tavasz', 'Tavaszi félév')


@login_required
def osz(request):
    return _naptar(request, 'Ősz', 'Őszi félév')
