"""Test data builders shared by the apps' test suites."""
import datetime
import os

from django.contrib.auth.models import Group, User

from faq.models import Kerdes
from mintatanterv import models as mt
from orarend.models import Beallitas as OrarendBeallitas, OrarendFajl
from szabalyzat.models import Szabalyzat
from szakdolgozat import models as sz
from tanulmanyi.permissions import OKTATOK_CSOPORT

D = datetime.date


def create_users():
    oktatok = Group.objects.get_or_create(name=OKTATOK_CSOPORT)[0]
    student = User.objects.create_user('student', password='x')
    oktato = User.objects.create_user('oktato', password='x')
    oktato.groups.add(oktatok)
    staff = User.objects.create_user('staff', password='x', is_staff=True)
    staff.groups.add(oktatok)
    return {'student': student, 'oktato': oktato, 'staff': staff}


class SzakdolgozatAdatok:
    """Supervisors with topic areas, titles in every status and students on them."""

    def __init__(self):
        self.statuszok = {}
        for i, nev in [(1, 'Szabad'), (2, 'Foglalt'), (3, 'Megírt'), (4, 'Szabad (elkezdett, de be nem fejezett)'),
                       (5, 'Visszavont'), (6, 'Címbejelentő lap kiadva')]:
            self.statuszok[i] = sz.TemaStatusz.objects.create(id=i, nev=nev)
        nappali = sz.Tagozat.objects.create(nev='nappali')
        levelezo = sz.Tagozat.objects.create(nev='levelező')
        self.kepzesek = [sz.Kepzes.objects.create(kepzes_kod='GTBA', kepzes_nev='Gazdálkodás BA', tagozat=nappali),
                         sz.Kepzes.objects.create(kepzes_kod='GTBAL', kepzes_nev='Gazdálkodás BA', tagozat=levelezo),
                         sz.Kepzes.objects.create(kepzes_kod='MTN', kepzes_nev='Menedzsment MA', tagozat=nappali)]
        self.hallgato_statuszok = [sz.Statusz.objects.create(nev='aktív'), sz.Statusz.objects.create(nev='passzív')]
        self.jegyek = [sz.ErdemJegy.objects.create(nev=n, ertek=e)
                       for n, e in [('elégtelen', 1), ('elégséges', 2), ('közepes', 3), ('jó', 4), ('jeles', 5)]]
        self.temakorok = [sz.Temakor.objects.create(cim='Témakör %d: %s' % (i, 'x' * (i * 20))) for i in range(5)]
        for nev, szoveg in [('temavalasztas_menete', '<p>Menet</p>'), ('kurzusok', '<p>Kurzusok</p>'),
                            ('zarovizsga_tetelek', '<p>Tételek</p>')]:
            sz.Beallitas.objects.create(nev=nev, szoveg=szoveg)
        self.temavezetok = 0
        self.temak = 0
        self.hallgatok = 0

    def temavezetok_hozzaadasa(self, db, temak_per_temakor=4):
        for _ in range(db):
            v = self.temavezetok
            self.temavezetok += 1
            tv = sz.Temavezeto.objects.create(
                elotag='Dr.' if v % 2 else '', vezeteknev='Vezető%03d' % (500 - v), keresztnev='Kereszt%d' % v,
                neptun_kod='TV%04d' % v, max_letszam=3 + v % 7, email='tv%d@bhf.hu' % v,
                avatott_nev='Avatott' if v % 3 == 0 else '', valaszthato=v % 4 != 1, inaktiv=v % 6 == 4, sorszam=v)
            for k in range(v % 3 + 1):
                tt = sz.TemavezetoTemakor.objects.create(temavezeto=tv, temakor=self.temakorok[(v + k) % 5],
                                                         rejtett=(v + k) % 5 == 2)
                for _ in range(temak_per_temakor):
                    self._tema(tt)

    def _tema(self, temavezeto_temakor):
        self.temak += 1
        n = self.temak
        tema = sz.Tema.objects.create(
            cim='Cím %04d %s' % (n, 'hosszú ' * (n % 4)), temavezeto_temakor=temavezeto_temakor,
            tema_statusz=self.statuszok[n % 6 + 1], idegen_nyelv_szukseges='angol' if n % 5 == 0 else '',
            megjegyzes='megj.' if n % 7 == 0 else '')
        for h in range(n % 3):
            self.hallgatok += 1
            m = self.hallgatok
            hallgato = sz.Hallgato.objects.create(elotag='', vezeteknev='Hallgató%04d' % (5000 - m),
                                                  keresztnev='H%d' % m, neptun_kod='H%05d' % m)
            hk = sz.HallgatoKepzes.objects.create(hallgato=hallgato, kepzes=self.kepzesek[m % 3], kezdet=D(2020, 9, 1),
                                                  statusz=self.hallgato_statuszok[m % 2])
            kesz = tema.tema_statusz_id == 3 and h == 0
            sz.HallgatoKepzesTema.objects.create(
                hallgato_kepzes=hk, tema=tema, kezdet=D(2021, 1 + m % 12, 1),
                veg=D(2023, 1 + m % 12, 15) if kesz or m % 4 == 0 else None,
                erdemjegy=self.jegyek[m % 5] if kesz else None,
                sikeres_vedes_datuma=D(2023, 6, 20) if kesz else None,
                szakdolgozat_targyat_felvett=m % 2 == 0,
                szakdolgozat_link='https://example.org/%d.pdf' % m if kesz and m % 2 else None)


class MintatantervAdatok:
    """Curricula with subjects, prerequisites and courses taught by several teachers."""

    def __init__(self):
        szintek = [mt.KepzesiSzint.objects.create(nev='alapképzés (BA)  '),
                   mt.KepzesiSzint.objects.create(nev='mesterképzés (MA)  ')]
        self.munkarendek = [mt.Munkarend.objects.create(nev='nappali'), mt.Munkarend.objects.create(nev='levelező')]
        self.kovetelmenyek = [mt.Kovetelmeny.objects.create(nev='kollokvium'),
                              mt.Kovetelmeny.objects.create(nev='gyakorlati jegy')]
        self.kurzustipusok = {i: mt.Kurzustipus.objects.create(id=i, nev=n) for i, n in
                              [(1, 'előadás'), (2, 'gyakorlat'), (3, 'szeminárium'), (4, 'vizsgakurzus')]}
        self.vizsgatipusok = [mt.Vizsgatipus.objects.create(nev='írásbeli'), mt.Vizsgatipus.objects.create(nev='szóbeli')]
        self.jegyzetfelelos = mt.Oktatotipus.objects.create(nev='Jegyzetfelelős')
        self.eloado = mt.Oktatotipus.objects.create(nev='Előadó')
        self.nyelvek = [mt.Nyelv.objects.create(id=1, nev='magyar'), mt.Nyelv.objects.create(id=2, nev='angol')]
        self.felveteli_tipusok = {i: mt.FelvetelTipusa.objects.create(id=i, nev=n) for i, n in
                                  [(1, 'kötelező'), (2, 'kötelezően választható'), (3, 'szabadon választható')]}
        mt.Felev.objects.create(felev='2025/26/1', aktualis=True)
        mt.Felev.objects.create(felev='2024/25/2', aktualis=False)

        self.oktatok = [mt.Oktato.objects.create(elotag='Dr.' if i % 2 else '', vezeteknev='Oktató%d' % (9 - i),
                                                 keresztnev='K%d' % i, neptun_kod='OK%04d' % i,
                                                 avatott_nev='Av' if i == 2 else '', email='o%d@bhf.hu' % i,
                                                 megjelenites=i != 3) for i in range(6)]
        kepzesek = [mt.Kepzes.objects.create(nev='Gazdálkodás', kepzesi_szint=szintek[0]),
                    mt.Kepzes.objects.create(nev='Menedzsment', kepzesi_szint=szintek[1])]
        szakok = [mt.Szak.objects.create(nev='Gazdálkodási és menedzsment', kepzes=kepzesek[0]),
                  mt.Szak.objects.create(nev='Kereskedelem és marketing', kepzes=kepzesek[0]),
                  mt.Szak.objects.create(nev='Vezetés és szervezés', kepzes=kepzesek[1])]
        specializaciok = [mt.Specializacio.objects.create(nev='Pénzügy', szak=szakok[0]),
                          mt.Specializacio.objects.create(nev='HR', szak=szakok[0])]
        szakiranyok = [mt.Szakirany.objects.create(nev='Marketing', szak=szakok[1]),
                       mt.Szakirany.objects.create(nev='Árva', szak=None)]
        csoportok = [mt.NagyTargyCsoport.objects.create(nev='Alap', szak=szakok[0]),
                     mt.NagyTargyCsoport.objects.create(nev='Szakmai', szak=szakok[2])]
        self.nagytargyak = []
        for i in range(3):
            nagytargy = mt.NagyTargy.objects.create(targykod='NT%d' % i, targynev='Nagytárgy %d' % i, kredit=10)
            nagytargy.nagytargycsoport.add(csoportok[i % 2])
            self.nagytargyak.append(nagytargy)

        self.mintatantervek = [mt.Mintatanterv.objects.create(kod='GM17', nev='Gazdálkodás 2017', aktualis=True),
                               mt.Mintatanterv.objects.create(kod='J14', nev='Kereskedelem 2014', aktualis=True),
                               mt.Mintatanterv.objects.create(kod='MT17', nev='Menedzsment 2017', aktualis=False)]
        self.mintatantervek[0].szak.add(szakok[0])
        self.mintatantervek[0].specializacio.add(specializaciok[0])
        self.mintatantervek[1].szak.add(szakok[1])
        self.mintatantervek[1].szakirany.add(szakiranyok[0])
        self.mintatantervek[2].szak.add(szakok[2])
        self.mintatantervek[2].specializacio.add(specializaciok[1])

        self.targyak = []
        self.targyak_hozzaadasa(20)
        for i in range(0, 20, 6):
            self.targyak[i].ekvivalens_targy.add(self.targyak[i + 1])
        for i in range(3, 20, 4):
            mt.Elofeltetel.objects.create(targy=self.targyak[i], elofeltetel_targy=self.targyak[i - 3],
                                          eros_elofeltetel=i % 8 == 3)
            mt.Elofeltetel.objects.create(targy=self.targyak[i], elofeltetel_targy=self.targyak[i - 2])
        for m, tanterv in enumerate(self.mintatantervek):
            self.mintatantervbe(tanterv, [self.targyak[(j * 3 + m * 5) % 20] for j in range(12)], eltolas=m)

    def targyak_hozzaadasa(self, db):
        """Creates subjects, each with courses (daytime and most also correspondence) and a responsible teacher."""
        ujak = []
        for _ in range(db):
            i = len(self.targyak)
            targy = mt.Targy.objects.create(targykod='T%03d' % (500 - i), targynev='Tárgy %d' % i, kredit=2 + i % 5,
                                            kovetelmeny=self.kovetelmenyek[i % 2] if i % 7 else None)
            targy.kurzustipus.add(self.kurzustipusok[1 + i % 3])
            if i % 4 == 0:
                targy.kurzustipus.add(self.kurzustipusok[2])
            targy.nagytargy.add(self.nagytargyak[i % 3])
            for munkarend, jel in zip(self.munkarendek, 'NL'):
                if jel == 'L' and i % 3 == 0:
                    continue
                kurzus = mt.TargyMunkarend.objects.create(
                    targy=targy, kurzuskod='%s-%s%s' % (targy.targykod, jel, '-KV' if i % 9 == 4 else ''),
                    munkarend=munkarend, orarend_oraszam=[0, 4, 7, 14][i % 4], max_hianyzas=[0, 1, 2, 5][i % 4],
                    akkr_oraszam=28 + i, max_letszam=None if i % 6 == 5 else 20 + i,
                    kurzustipus=(self.kurzustipusok[4] if i % 10 == 7
                                 else None if i % 11 == 3 else self.kurzustipusok[1 + i % 3]),
                    nyelv=self.nyelvek[1 if i % 8 == 1 else 0], nem_indul=i % 13 == 12,
                    megjegyzes='m' if i % 3 else None, lejelentkezes_letiltva=i % 2 == 0)
                kurzus.oktato.add(self.oktatok[i % 6])
                if i % 5 == 0:
                    kurzus.oktato.add(self.oktatok[(i + 1) % 6])
                kurzus.vizsgatipus.add(self.vizsgatipusok[i % 2])
            mt.TargyOktato.objects.create(targy=targy, oktato=self.oktatok[i % 4],
                                          oktato_tipus=self.jegyzetfelelos if i % 2 else self.eloado)
            self.targyak.append(targy)
            ujak.append(targy)
        return ujak

    def mintatantervbe(self, mintatanterv, targyak, eltolas=0):
        """Adds subjects to a curriculum, every third one with a curriculum-specific prerequisite."""
        mtts = [mt.MintatantervTargy.objects.create(
            mintatanterv=mintatanterv, targy=targy, felev=1 + (j + eltolas) % 6,
            kredit=(4 + j % 3) if j % 4 == 0 else None, felvetel_tipusa=self.felveteli_tipusok[1 + (j * 7) % 3],
            oszi_tavaszi=j % 5 == 0) for j, targy in enumerate(targyak)]
        for j, mtt in enumerate(mtts):
            if j % 3 == 0:
                mt.ElofeltetelMintatantervben.objects.create(targy=mtt, elofeltetel_targy=targyak[(j + 1) % len(targyak)],
                                                             eros_elofeltetel=j % 2 == 0)
        return mtts


TEACHERS_HTML = '''<html><body>
<ul>
<li><a href="#table_1">Tanár Anna</a></li>
<li><a href="#table_2">Tanár Béla</a></li>
</ul>
<table id="table_1" border="1"><caption>Tanár Anna</caption>
<tr><th rowspan="2">Tanár Anna</th><th>Hétfő</th><th>Kedd</th></tr>
<tr><td rowspan="3">8:00</td><td>Mikro {week}<div class="studentsset">1A</div></td></tr>
<tr><td>9:00</td><td>Makro</td></tr>
</table>
<p>Vissza</p>
<table id="table_2" border="1"><caption>Tanár Béla</caption>
<tr><th rowspan="2">Tanár Béla</th><th>Hétfő</th><th>Kedd</th></tr>
<tr><td rowspan="2">8:00</td><td>Jog {week}<div class="studentsset">2B</div></td></tr>
</table>
</body></html>'''

YEARS_HTML = '''<html><body>
<ul>
<li><a href="#table_1">1. évfolyam</a></li>
<li><a href="#table_2">2. évfolyam</a></li>
</ul>
<table id="table_1" border="1"><caption>1. évfolyam</caption>
<tr><th rowspan="2">1. évfolyam</th><th>Hétfő</th></tr>
<tr><td rowspan="4">8:00</td><td>Statisztika {week}<div class="studentsset">1A</div></td></tr>
</table>
<p class="megjegyzes">Megjegyzés {week}</p>
<table id="table_2" border="1"><caption>2. évfolyam</caption>
<tr><th rowspan="2">2. évfolyam</th><th>Hétfő</th></tr>
<tr><td rowspan="2">8:00</td><td>Pénzügy {week}</td></tr>
</table>
</body></html>'''


def create_orarend(media_root, hetek=2):
    """Uploads weekly timetable exports (teachers' and year groups') into media_root."""
    os.makedirs(os.path.join(media_root, 'orarendek'), exist_ok=True)
    for week in range(1, hetek + 1):
        for kind, html, oktatoi in [('teachers', TEACHERS_HTML, True), ('years', YEARS_HTML, False)]:
            name = 'orarendek/het%d_%s_days_horizontal.html' % (week, kind)
            with open(os.path.join(media_root, name), 'w') as f:
                f.write(html.format(week=week))
            OrarendFajl.objects.create(orarendfajl=name, oktatoi_orarendfajl=oktatoi, aktiv=True)
    OrarendFajl.objects.create(orarendfajl='orarendek/inaktiv.html', oktatoi_orarendfajl=False, aktiv=False)
    OrarendBeallitas.objects.create(nev='Szünet', ertek='2')
    OrarendBeallitas.objects.create(nev='Ősz', ertek='oszi-sheet-id')
    OrarendBeallitas.objects.create(nev='Tavasz', ertek='tavaszi-sheet-id')


def create_szabalyzatok_es_kerdesek(media_root):
    os.makedirs(os.path.join(media_root, 'szabalyzatok'), exist_ok=True)
    for i, (nev, csak) in enumerate([('Tanulmányi szabályzat', False), ('Oktatói kézikönyv', True),
                                     ('Térítési szabályzat', False)]):
        name = 'szabalyzatok/szabalyzat_%d.pdf' % i
        with open(os.path.join(media_root, name), 'wb') as f:
            f.write(b'%PDF-1.4 fake ' + nev.encode())
        Szabalyzat.objects.create(nev=nev, szabalyzatfajl=name, csak_oktatoknak=csak)
    Kerdes.objects.create(kerdes='Hogyan jelentkezem?', valasz='<p>Így.</p>', publikalt=True)
    Kerdes.objects.create(kerdes='Rejtett kérdés?', valasz='<p>Nem.</p>', publikalt=False)
