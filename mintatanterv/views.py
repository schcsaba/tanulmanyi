import io
from collections import defaultdict

from xlsxwriter.workbook import Workbook
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Q
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from mintatanterv.models import (Kepzes, Szak, Mintatanterv, Specializacio, Szakirany, MintatantervTargy, TargyMunkarend,
                                 Oktato, Targy, Felev, TargyOktato, Elofeltetel, ElofeltetelMintatantervben)
from tanulmanyi.permissions import oktato_required

KOTELEZO = 1  # FelvetelTipusa id
VIZSGAKURZUS = 4  # Kurzustipus id
JEGYZETFELELOS = 'Jegyzetfelelős'  # Oktatotipus név

FELEVEK = {
    'osz': {
        'felevek': [1, 3, 5],
        'oktatok_cim': 'Az őszi félév kurzusainak oktatói',
        'melleknev': 'őszi',
        'lista_url': 'oktatok_kurzusai_osz',
        'oktato_url': 'oktato_kurzusai_osz',
        'xlsx_url': 'xlsx_oktatok_kurzusai_osz',
        'xlsx_nev': 'oszi_kurzusok',
    },
    'tavasz': {
        'felevek': [2, 4, 6],
        'oktatok_cim': 'A tavaszi félév kurzusainak oktatói',
        'melleknev': 'tavaszi',
        'lista_url': 'oktatok_kurzusai_tavasz',
        'oktato_url': 'oktato_kurzusai_tavasz',
        'xlsx_url': 'xlsx_oktatok_kurzusai_tavasz',
        'xlsx_nev': 'tavaszi_kurzusok',
    },
}

# Mintatanterv kód -> Neptun kód; a (levelező, nappali) pár, ha a kurzus munkarendjétől függ
NEPTUN_MINTATANTERV_KODOK = {
    'KJJBA17': 'KJJBA',
    'KJTBA17': 'KJTBA',
    'KJTMA17': 'KJTMA',
    'SZAJBA17': ('SZAJBA17-L', 'SZAJBA17-N'),
    'J09': ('JL09', 'JN09'),
    'J12': ('JL12', 'JN12'),
    'J13': ('JL13', 'JN13'),
    'J14': ('JL14', 'JN14'),
    'J15': ('JL15', 'JN15'),
    'J17': ('JL17', 'JN17'),
    'T13': ('TL13', 'TN13'),
    'T15': ('TL15', 'TN15'),
    'T16': ('TL16', 'TN16'),
    'T17': ('TL17', 'TN17'),
    'MT14': 'MTN14',
    'MT14J': 'MTN14J',
    'MT14T': 'MTN14T',
    'MT17': 'MTN17',
    'MT17J': 'MTN17J',
    'MT17T': 'MTN17T',
}

XLSX_FEJLEC = ['Tárgykód', 'Félév', 'Kurzuskód', 'Maximális létszám', 'Nyelv', 'Kurzustípus', 'Megjegyzés',
               'Heti óraszám', 'Féléves óraszám', 'Típusazonosító', 'Lejelentkezés letiltva', 'Jelentkezés letiltva',
               'Kurzusfelvételi követelmény', 'Kurzusfelvételi követelmény leírás', 'Tagozat',
               'Alkalmazott Neptun kódja', 'Mintatanterv kódja']


def _aktualis_felev():
    try:
        return Felev.objects.get(aktualis=True).felev
    except Felev.DoesNotExist:
        return 'Nincs megadva'
    except Felev.MultipleObjectsReturned:
        return 'Több is meg van adva'


def _felev_kurzusai(felev):
    """The courses that run in the given semester of the current curricula."""
    return TargyMunkarend.objects.exclude(nem_indul=True).filter(
        Q(targy__mintatanterv__aktualis=True),
        Q(targy__mintatantervtargy__felev__in=FELEVEK[felev]['felevek'])
        | Q(targy__mintatantervtargy__oszi_tavaszi=True)
        | Q(kurzustipus=VIZSGAKURZUS)).distinct()


def _neptun_mintatanterv_kod(mintatanterv, kurzus):
    kod = NEPTUN_MINTATANTERV_KODOK.get(mintatanterv.kod, mintatanterv.kod)
    if isinstance(kod, tuple):
        levelezo, nappali = kod
        return levelezo if kurzus.munkarend.nev == 'levelező' else nappali
    return kod


@login_required
def mintatantervek(request):
    def mintatantervei(kapcsolat):
        return Prefetch(kapcsolat, queryset=Mintatanterv.objects.all(), to_attr='mintatantervek')

    szakok = Szak.objects.order_by('pk').prefetch_related(
        mintatantervei('mintatantervszak'),
        Prefetch('specializacio_set', to_attr='specializaciok',
                 queryset=Specializacio.objects.order_by('pk').prefetch_related(mintatantervei('mintatantervspecializacio'))),
        Prefetch('szakirany_set', to_attr='szakiranyok',
                 queryset=Szakirany.objects.order_by('pk').prefetch_related(mintatantervei('mintatantervszakirany'))))
    kepzesek = (Kepzes.objects.select_related('kepzesi_szint').order_by('pk')
                .prefetch_related(Prefetch('szak_set', queryset=szakok, to_attr='szakok')))
    return render(request, 'mintatanterv/mintatantervek.html', {'kepzesek': kepzesek})


@login_required
def mintatanterv(request, mintatanterv_id):
    mintatanterv = get_object_or_404(Mintatanterv, pk=mintatanterv_id)
    kurzusok = (TargyMunkarend.objects.select_related('munkarend', 'kurzustipus')
                .prefetch_related('oktato', 'vizsgatipus').order_by('pk'))
    mintatantervtargyak = list(
        mintatanterv.mintatantervtargy_set
        .select_related('targy__kovetelmeny', 'felvetel_tipusa')
        .prefetch_related(
            Prefetch('fotargymintatantervben', queryset=ElofeltetelMintatantervben.objects
                     .select_related('elofeltetel_targy').order_by('elofeltetel_targy_id')),
            Prefetch('targy__fotargy', queryset=Elofeltetel.objects
                     .select_related('elofeltetel_targy').order_by('elofeltetel_targy_id')),
            'targy__kurzustipus',
            Prefetch('targy__targymunkarend_set', queryset=kurzusok))
        # Within a felvétel típusa MySQL used to return them in tárgy order; kept explicit.
        .order_by('felvetel_tipusa', 'targy_id'))

    # Which subjects of this curriculum each subject is a prerequisite of
    targy_idk = [mtt.targy_id for mtt in mintatantervtargyak]
    melyik_targynak = defaultdict(list)
    for elofeltetel in (Elofeltetel.objects.filter(elofeltetel_targy__in=targy_idk, targy__in=targy_idk)
                        .select_related('targy').order_by('targy__targykod')):
        melyik_targynak[elofeltetel.elofeltetel_targy_id].append(elofeltetel.targy)
    melyik_mintatantervtargynak = defaultdict(list)
    for elofeltetel in (ElofeltetelMintatantervben.objects
                        .filter(elofeltetel_targy__in=targy_idk, targy__mintatanterv=mintatanterv)
                        .select_related('targy__targy').order_by('pk')):
        melyik_mintatantervtargynak[elofeltetel.elofeltetel_targy_id].append(elofeltetel.targy)

    felevek = sorted({mtt.felev for mtt in mintatantervtargyak})
    felev_kreditek = dict.fromkeys(felevek, 0)
    felev_nem_kot_kreditek = dict.fromkeys(felevek, 0)
    for mtt in mintatantervtargyak:
        kreditek = felev_kreditek if mtt.felvetel_tipusa_id == KOTELEZO else felev_nem_kot_kreditek
        kreditek[mtt.felev] += mtt.kredit or mtt.targy.kredit
        mtt.melytargyelofeltetele = melyik_targynak[mtt.targy_id]
        mtt.melymintatantervtargyelofeltetele = melyik_mintatantervtargynak[mtt.targy_id]

    args = {}
    args['mintatanterv'] = mintatanterv
    args['felevek'] = felevek
    args['felev_kreditek'] = felev_kreditek
    args['felev_nem_kot_kreditek'] = felev_nem_kot_kreditek
    args['mintatantervtargyak'] = mintatantervtargyak
    return render(request, 'mintatanterv/mintatanterv.html', args)


@oktato_required
def oktatok_kurzusai(request, felev):
    kurzusok = _felev_kurzusai(felev).exclude(kurzuskod__icontains='-KV')
    oktatok = Oktato.objects.filter(pk__in=kurzusok.values_list('oktato', flat=True))
    return render(request, 'mintatanterv/oktatok_kurzusai.html', {'oktatok': oktatok, 'felev': FELEVEK[felev]})


@oktato_required
def oktato_kurzusai(request, felev, oktato_id):
    oktato = get_object_or_404(Oktato, pk=oktato_id)
    oktato_kurzusai = _felev_kurzusai(felev).exclude(kurzuskod__icontains='-KV').filter(oktato=oktato)
    kurzusok = (oktato_kurzusai.select_related('targy', 'munkarend', 'kurzustipus')
                .prefetch_related('vizsgatipus').order_by('pk'))
    aktualis_mintatantervtargyak = (MintatantervTargy.objects.filter(mintatanterv__aktualis=True)
                                    .select_related('mintatanterv', 'felvetel_tipusa').order_by('mintatanterv__kod'))
    targyak = list(Targy.objects.filter(pk__in=oktato_kurzusai.values_list('targy', flat=True))
                   .select_related('kovetelmeny')
                   .prefetch_related('kurzustipus', 'ekvivalens_targy',
                                     Prefetch('mintatantervtargy_set', queryset=aktualis_mintatantervtargyak,
                                              to_attr='aktualis_mintatantervtargyak')))

    targy_kurzusai = defaultdict(list)
    for kurzus in kurzusok:
        targy_kurzusai[kurzus.targy_id].append(kurzus)
    for targy in targyak:
        mtts = targy.aktualis_mintatantervtargyak
        targy.felev_kurzusai = targy_kurzusai[targy.pk]
        targy.mintatantervi_kredit = ['%s: %s' % (m.mintatanterv.kod, m.kredit) for m in mtts if m.kredit]
        targy.mintatantervek_felevekkel = ['%s: %s. félév' % (m.mintatanterv.kod, m.felev) for m in mtts]
        targy.mintatantervek_felvetel_tipusaval = ['%s: %s' % (m.mintatanterv.kod, m.felvetel_tipusa) for m in mtts]

    args = {}
    args['oktato'] = oktato
    args['targyak'] = targyak
    args['felev'] = FELEVEK[felev]
    return render(request, 'mintatanterv/oktato_kurzusai.html', args)


@staff_member_required
def xlsx_oktatok_kurzusai(request, felev):
    kurzusok = (_felev_kurzusai(felev)
                .select_related('targy', 'munkarend', 'nyelv', 'kurzustipus')
                .prefetch_related('oktato', Prefetch('targy__mintatanterv', to_attr='aktualis_mintatantervek',
                                                     queryset=Mintatanterv.objects.filter(aktualis=True)))
                .order_by('pk'))
    aktualis_felev = _aktualis_felev()

    output = io.BytesIO()
    book = Workbook(output)
    sheet = book.add_worksheet(FELEVEK[felev]['xlsx_nev'])
    sheet.write_row(0, 0, XLSX_FEJLEC)
    x = 1
    for kurzus in kurzusok:
        for mintatanterv in kurzus.targy.aktualis_mintatantervek:
            mintatanterv_kod = _neptun_mintatanterv_kod(mintatanterv, kurzus)
            for oktato in kurzus.oktato.all():
                sheet.write(x, 0, kurzus.targy.targykod)
                sheet.write(x, 1, aktualis_felev)
                sheet.write(x, 2, kurzus.kurzuskod)
                sheet.write(x, 3, kurzus.max_letszam)
                if kurzus.nyelv:
                    sheet.write(x, 4, kurzus.nyelv.nev)
                if kurzus.kurzustipus:
                    sheet.write(x, 5, kurzus.kurzustipus.nev)
                sheet.write(x, 6, kurzus.megjegyzes)
                sheet.write(x, 7, round(float(kurzus.akkr_oraszam) / 15, 1))
                sheet.write(x, 8, kurzus.akkr_oraszam)
                if kurzus.kurzustipus:
                    sheet.write(x, 9, 'Vizsgakurzus' if kurzus.kurzustipus.id == VIZSGAKURZUS else 'Normál')
                sheet.write(x, 10, kurzus.lejelentkezes_letiltva)
                sheet.write(x, 11, kurzus.jelentkezes_letiltva)
                sheet.write(x, 12, kurzus.kurzusfelveteli_kovetelmeny)
                sheet.write(x, 13, kurzus.kurzusfelveteli_kovetelmeny_leiras)
                sheet.write(x, 14, kurzus.munkarend.nev)
                sheet.write(x, 15, oktato.neptun_kod)
                sheet.write(x, 16, mintatanterv_kod)
                x += 1
    book.close()

    output.seek(0)
    response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=%s_listaja.xlsx" % FELEVEK[felev]['xlsx_nev']

    return response


@staff_member_required
def kurzus_naplo(request, kurzus_id):
    kurzus = get_object_or_404(TargyMunkarend, pk=kurzus_id)
    munkarend = kurzus.munkarend
    kurzustipus = kurzus.kurzustipus
    targy = kurzus.targy
    ekvivalens_targyak = targy.ekvivalens_targy.all()
    targyak = []
    targyak.append(targy)
    kurzusok = []
    kurzusok.append(kurzus)

    for ekvivalens_targy in ekvivalens_targyak:
        targyak.append(ekvivalens_targy)
        ekv_targy_kurzusai = ekvivalens_targy.targymunkarend_set.filter(munkarend=munkarend).filter(kurzustipus=kurzustipus).exclude(kurzuskod__contains='-KV')
        for ekv_targy_kurzus in ekv_targy_kurzusai:
            kurzusok.append(ekv_targy_kurzus)

    oktatok = []
    oktatok1 = []
    kurzuskodok = []

    for kurzus in kurzusok:
        kurzus_oktatoi = kurzus.oktato.all().values_list('vezeteknev', 'keresztnev')
        kurzus_oktatoi_veznevek = kurzus.oktato.all().values_list('vezeteknev', flat=True)
        kurzuskodok.append(kurzus.kurzuskod)

        for kurzus_oktato in kurzus_oktatoi:
            oktatok.append(' '.join(kurzus_oktato))

        for kurzus_oktato_veznev in kurzus_oktatoi_veznevek:
            oktatok1.append(kurzus_oktato_veznev)

        szakok = []

        nagytargyak = kurzus.targy.nagytargy.all()

        for nagytargy in nagytargyak:
            nagytargy_nagytargycsoportok = nagytargy.nagytargycsoport.all()

            for nagytargy_nagytargycsoport in nagytargy_nagytargycsoportok:
                szakok.append(nagytargy_nagytargycsoport.szak.nev[9].upper() + ' (' + nagytargy_nagytargycsoport.szak.kepzes.kepzesi_szint.nev[-7:-5] + ')')

        szakok = sorted(set(szakok))
        szakok = ', '.join(szakok)
        kurzus.szakok = szakok

    oktatok = sorted(set(oktatok))
    oktatok = ', '.join(oktatok)
    oktatok1 = sorted(set(oktatok1))
    oktatok1 = '_'.join(oktatok1)
    kurzuskodok = '_'.join(kurzuskodok)

    felev = _aktualis_felev()

    targylista = []

    for targy in targyak:
        targylista.append(targy.__str__())

    targylista = '\n'.join(targylista)

    output = io.BytesIO()
    book = Workbook(output)
    sheet = book.add_worksheet(kurzus.kurzuskod)
    sheet.set_row(0, 31.5)
    sheet.set_row(3, 45.75)
    sheet.set_row(10, 30)
    sheet.set_row(11, 5)
    sheet.set_row(13, 33)
    sheet.set_column(0, 0, 2.29)
    sheet.set_column(2, 2, 19.43)
    sheet.set_column(3, 100, 4.86)
    format = book.add_format()
    format.set_font_size(24)
    sheet.merge_range('B1:D1', 'Jelenléti ív', format)
    format = book.add_format()
    format.set_bold()
    format.set_align('right')
    format.set_align('vcenter')
    format.set_border(1)
    format.set_text_wrap()
    sheet.merge_range('B2:C2', 'Oktató(k)', format)
    format1 = book.add_format()
    format1.set_align('center')
    format1.set_align('vcenter')
    format1.set_border(1)
    format1.set_text_wrap()
    sheet.merge_range('D2:I2', oktatok, format1)
    sheet.merge_range('B3:C3', 'Félév', format)
    sheet.merge_range('D3:I3', felev, format1)
    sheet.merge_range('B4:C4', 'Tárgy(ak)', format)
    if kurzustipus:
        sheet.merge_range('D4:I4', targylista + '\n' + '(' + kurzustipus.__str__() + ')', format1)
    else:
       sheet.merge_range('D4:I4', targylista + '\n' + '(Kurzustípus nincs megadva)', format1)
    sheet.merge_range('B5:C5', 'Szak', format)
    x = 'D'
    y = 'E'
    z = 0
    letszam = 0
    for kurzus in kurzusok:
        sheet.merge_range(x + '5:' + y + '5', kurzus.szakok, format1)
        sheet.merge_range(x + '6:' + y + '6', kurzus.kurzuskod, format1)
        sheet.merge_range(x + '7:' + y + '7', kurzus.orarend_oraszam, format1)
        if kurzus.orarend_oraszam > 0:
            if kurzus.max_hianyzas / kurzus.orarend_oraszam * 100 == 0:
                hianyzas_aranya = 0
            elif kurzus.max_hianyzas / kurzus.orarend_oraszam * 100 < 34:
                hianyzas_aranya = 20
            else:
                hianyzas_aranya = 40
            sheet.merge_range(x + '8:' + y + '8', str(hianyzas_aranya) + '%', format1)
        else:
            sheet.merge_range(x + '8:' + y + '8', '-', format1)
        sheet.merge_range(x + '9:' + y + '9', kurzus.max_hianyzas, format1)
        sheet.merge_range(x + '10:' + y + '10', '', format1)
        sheet.merge_range(x + '11:' + y + '11', '', format1)
        x = chr(ord(x) + 2)
        y = chr(ord(y) + 2)
        z += 1
        if kurzus.max_letszam:
            letszam = letszam + kurzus.max_letszam
        else:
            letszam = 3
    if z < 3:
        a = 3 - z
        for i in range(a):
            sheet.merge_range(x + '5:' + y + '5', '', format1)
            sheet.merge_range(x + '6:' + y + '6', '', format1)
            sheet.merge_range(x + '7:' + y + '7', '', format1)
            sheet.merge_range(x + '8:' + y + '8', '', format1)
            sheet.merge_range(x + '9:' + y + '9', '', format1)
            sheet.merge_range(x + '10:' + y + '10', '', format1)
            sheet.merge_range(x + '11:' + y + '11', '', format1)
            x = chr(ord(x) + 2)
            y = chr(ord(y) + 2)
    sheet.merge_range('B6:C6', 'Kurzuskód', format)
    sheet.merge_range('B7:C7', 'Mintatanterv szerinti óraszám', format)
    sheet.merge_range('B8:C8', 'Megengedett hiányzás aránya', format)
    sheet.merge_range('B9:C9', 'Megengedett hiányzás', format)
    sheet.merge_range('B10:C10', 'Ténylegesen megtartott óraszám', format)
    sheet.merge_range('B11:C11', 'Megengedett hiányzás a tényleges óraszám alapján', format)
    format2 = book.add_format()
    format2.set_bold()
    format2.set_align('center')
    format2.set_align('vcenter')
    format2.set_left(5)
    format2.set_bottom(5)
    format2.set_top(1)
    format2.set_right(1)
    sheet.merge_range('B14:C14', 'Hallgatók', format2)
    b = 14
    for i in range(letszam):
        sheet.write(b, 0, i + 1)
        sheet.merge_range('B' + str(b + 1) + ':C' + str(b + 1), '', format)
        sheet.set_row(b, 22.5)
        d = 3
        for c in range(kurzus.orarend_oraszam):
            sheet.merge_range(b, d, b, d + 1, '', format1)
            d += 2
        b += 1
    format3 = book.add_format()
    format3.set_bg_color('#BFBFBF')
    format3.set_left(5)
    format3.set_top(5)
    format3.set_bottom(1)
    format3.set_right(1)
    sheet.merge_range('B13:C13', '', format3)
    format5 = book.add_format()
    format5.set_right(1)
    format5.set_top(1)
    format5.set_bottom(5)
    format5.set_left(1)
    format6 = book.add_format()
    format6.set_right(5)
    format6.set_top(1)
    format6.set_bottom(5)
    format6.set_left(1)
    d = 3
    for e in range(kurzus.orarend_oraszam):
        if e + 1 == kurzus.orarend_oraszam:
            sheet.merge_range(13, d, 13, d + 1, '', format6)
        else:
            sheet.merge_range(13, d, 13, d + 1, '', format5)
        d += 2
    format4 = book.add_format()
    format4.set_bold()
    format4.set_align('center')
    format4.set_align('vcenter')
    format4.set_right(5)
    format4.set_top(5)
    format4.set_bottom(1)
    format4.set_left(1)
    sheet.merge_range(12, 3, 12, d - 1, 'Dátum', format4)
    book.close()
    output.seek(0)
    response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=" + oktatok1 + "_" + kurzuskodok + ".xlsx"

    return response


@oktato_required
def jegyzetfelelosok(request):
    jegyzetfelelosok = Oktato.objects.filter(pk__in=TargyOktato.objects.filter(oktato_tipus__nev=JEGYZETFELELOS).values_list('oktato', flat=True).distinct())

    args = {}
    args['jegyzetfelelosok'] = jegyzetfelelosok
    return render(request, 'mintatanterv/jegyzetfelelosok.html', args)


@oktato_required
def jegyzetfelelos_targyai(request, oktato_id):
    oktato = get_object_or_404(Oktato, pk=oktato_id)
    targyak = Targy.objects.filter(pk__in=TargyOktato.objects.filter(Q(oktato=oktato), Q(oktato_tipus__nev=JEGYZETFELELOS)).values_list('targy', flat=True).distinct())

    args = {}
    args['targyak'] = targyak
    args['oktato'] = oktato
    return render(request, 'mintatanterv/jegyzetfelelos_targyai.html', args)


@login_required
def oktatok_elerhetosegei(request):
    args = {}
    oktatok = Oktato.objects.filter(megjelenites=True).order_by('vezeteknev', 'keresztnev')
    args['oktatok'] = oktatok
    return render(request, 'mintatanterv/oktatok_elerhetosegei.html', args)
