#from urllib.request import urlopen
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orarend.models import Beallitas, OrarendFajl

@login_required
def orarendi_oktatok(request):
    args = {}
    if OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=True).count() > 0:
        soup = BeautifulSoup(open(OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=True)[0].orarendfajl.path), 'html.parser')
        oktatok = soup.find_all('li')
        oktato_nevek = []
        for oktato in oktatok:
            oktato_nevek.append(oktato.string)
        args['oktato_nevek'] = oktato_nevek
    else:
        args['visszajelzes'] = 'Az órarend még nem érhető el.'
        args['title'] = 'Türelmét kérjük!'

    return render(request, 'orarend/orarendi_oktatok.html', args)


@login_required
def oktato_orarendje(request, oktato_id):
    args = {}
    if OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=True).count() > 0 and Beallitas.objects.filter(nev='Szünet').count() == 1:
        fajlok = OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=True).order_by('orarendfajl')
        orarendek = []
        for fajl in fajlok:
            soup = BeautifulSoup(open(fajl.orarendfajl.path), 'html.parser')
            oktatok = soup.find_all('li')
            orarend = soup.find(id=oktatok[int(oktato_id)].find('a')['href'][1:])
            [x.extract() for x in orarend('caption')]
            [x.extract() for x in orarend('div', {'class':'studentsset'})]
            orarend.th.extract() # Eltávolítja az oktató nevét.
            orarend.td['rowspan'] = '1'
            tag = soup.new_tag('th')
            orarend.th.insert_before(tag)
            orarend.tr.extract()
            orarendek.append(orarend.prettify())
        args['oktato_neve'] = oktatok[int(oktato_id)].string
        args['orarendek'] = orarendek
        args['szunet'] = int(Beallitas.objects.get(nev='Szünet').ertek)
    else:
        args['visszajelzes'] = 'Az órarend még nem érhető el.'
        args['title'] = 'Türelmét kérjük!'

    return render(request, 'orarend/oktato_orarendje.html', args)


@login_required
def evfolyamok(request):
    args = {}
    if OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=False).count() > 0:
        soup = BeautifulSoup(open(OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=False)[0].orarendfajl.path), 'html.parser')
        evfolyamok = soup.find_all('li')
        evfolyam_nevek = []
        for evfolyam in evfolyamok:
            evfolyam_nevek.append(evfolyam.a.string)
        args['evfolyam_nevek'] = evfolyam_nevek
    else:
        args['visszajelzes'] = 'Az órarend még nem érhető el.'
        args['title'] = 'Türelmét kérjük!'

    return render(request, 'orarend/evfolyamok.html', args)


@login_required
def evfolyam_orarendje(request, evfolyam_id):
    args = {}
    if OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=False).count() > 0 and Beallitas.objects.filter(nev='Szünet').count() == 1:
        fajlok = OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=False).order_by('orarendfajl')
        orarendek = []
        soup_megj = BeautifulSoup(open(OrarendFajl.objects.filter(aktiv=True).filter(oktatoi_orarendfajl=False)[0].orarendfajl.path), 'html.parser')
        megjegyzesek = soup_megj.table.next_sibling.next_sibling.prettify()
        for fajl in fajlok:
            soup = BeautifulSoup(open(fajl.orarendfajl.path), 'html.parser')
            evfolyamok = soup.find_all('li')
            orarend = soup.find(id=evfolyamok[int(evfolyam_id)].find('a')['href'][1:])
            [x.extract() for x in orarend('caption')]
            [x.extract() for x in orarend('div', {'class':'studentsset'})]
            orarend.th.extract() # Eltávolítja az évfolyam nevét.
            orarend.td['rowspan'] = '1'
            tag = soup.new_tag('th')
            orarend.th.insert_before(tag)
            orarend.tr.extract()
            orarendek.append(orarend.prettify())

        args['evfolyam_neve'] = evfolyamok[int(evfolyam_id)].a.string
        args['orarendek'] = orarendek
        args['szunet'] = int(Beallitas.objects.get(nev='Szünet').ertek)
        args['megjegyzesek'] = megjegyzesek

    else:
        args['visszajelzes'] = 'Az órarend még nem érhető el.'
        args['title'] = 'Türelmét kérjük!'

    return render(request, 'orarend/evfolyam_orarendje.html', args)


@login_required
def tavasz(request):
    args = {}
    if Beallitas.objects.filter(nev='Tavasz').count() == 1:
        args['naptar'] = Beallitas.objects.get(nev='Tavasz').ertek
        args['title'] = 'Tavaszi félév'

    else:
        args['visszajelzes'] = 'Az oktatási naptár még nem érhető el.'
        args['title'] = 'Türelmét kérjük!'

    args['cim'] = 'Tavaszi félév'

    return render(request, 'orarend/naptar.html', args)


@login_required
def osz(request):
    args = {}
    if Beallitas.objects.filter(nev='Ősz').count() == 1:
        args['naptar'] = Beallitas.objects.get(nev='Ősz').ertek
        args['title'] = 'Őszi félév'

    else:
        args['visszajelzes'] = 'Az oktatási naptár még nem érhető el.'
        args['title'] = 'Türelmét kérjük!'

    args['cim'] = 'Őszi félév'

    return render(request, 'orarend/naptar.html', args)