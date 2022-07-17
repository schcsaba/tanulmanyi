import io
from xlsxwriter.workbook import Workbook
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from mintatanterv.models import Kepzes, Szak, Mintatanterv, Specializacio, Szakirany, MintatantervTargy, TargyMunkarend, Oktato, Targy, Felev, TargyOktato

@login_required
def mintatantervek(request):
    args = {}
    kepzesek = Kepzes.objects.all()
    for kepzes in kepzesek:
        kepzes.szakok = Szak.objects.filter(kepzes=kepzes)
        for szak in kepzes.szakok:
            szak.mintatantervek = Mintatanterv.objects.filter(szak=szak)
            szak.specializaciok = Specializacio.objects.filter(szak=szak)
            for spec in szak.specializaciok:
                spec.mintatantervek = Mintatanterv.objects.filter(specializacio=spec)
            szak.szakiranyok = Szakirany.objects.filter(szak=szak)
            for szaki in szak.szakiranyok:
                szaki.mintatantervek = Mintatanterv.objects.filter(szakirany=szaki)
    args['kepzesek'] = kepzesek
    return render(request, 'mintatanterv/mintatantervek.html', args)


@login_required
def mintatanterv(request, mintatanterv_id):
    mintatanterv = get_object_or_404(Mintatanterv, pk=mintatanterv_id)
    args = {}
    args['mintatanterv'] = mintatanterv
    felevek = MintatantervTargy.objects.filter(mintatanterv=mintatanterv).order_by('felev').values_list('felev', flat=True).distinct()

    args['felevek'] = felevek

    felev_kreditek = {}
    felev_nem_kot_kreditek = {}
    for felev in felevek:
        felev_kotelezo_targyai = mintatanterv.mintatantervtargy_set.filter(felev=felev).filter(felvetel_tipusa=1)
        felev_nem_kotelezo_targyai = mintatanterv.mintatantervtargy_set.filter(felev=felev).exclude(felvetel_tipusa=1)
        felev_kredit = 0
        for felev_kotelezo_targy in felev_kotelezo_targyai:
            if felev_kotelezo_targy.kredit:
                felev_kredit = felev_kredit + felev_kotelezo_targy.kredit
            else:
                felev_kredit = felev_kredit + felev_kotelezo_targy.targy.kredit
        felev_kreditek[felev] = felev_kredit
        felev_nem_kot_kredit = 0
        for felev_nem_kotelezo_targy in felev_nem_kotelezo_targyai:
            if felev_nem_kotelezo_targy.kredit:
                felev_nem_kot_kredit = felev_nem_kot_kredit + felev_nem_kotelezo_targy.kredit
            else:
                felev_nem_kot_kredit = felev_nem_kot_kredit + felev_nem_kotelezo_targy.targy.kredit
        felev_nem_kot_kreditek[felev] = felev_nem_kot_kredit

    args['felev_kreditek'] = felev_kreditek
    args['felev_nem_kot_kreditek'] = felev_nem_kot_kreditek

    mintatantervtargyak = mintatanterv.mintatantervtargy_set.all().order_by('felvetel_tipusa')
    for mintatantervtargy in mintatantervtargyak:
        mintatantervtargy.melytargyelofeltetele = mintatantervtargy.targy.ezentargyakelofelteteletipussal.filter(mintatanterv=mintatanterv)
        mintatantervtargy.melymintatantervtargyelofeltetele = mintatantervtargy.targy.ezenmintatantervtargyakelofelteteletipussal.filter(mintatanterv=mintatanterv)

    args['mintatantervtargyak'] = mintatantervtargyak
    return render(request, 'mintatanterv/mintatanterv.html', args)


def in_oktatok_group(user):
    return user.is_authenticated and user.groups.filter(name='Oktatok').exists()


@user_passes_test(in_oktatok_group)
def oktatok_kurzusai_osz(request):
    kurzusok = TargyMunkarend.objects.exclude(kurzuskod__icontains='-KV').exclude(nem_indul=True).filter(Q(targy__mintatanterv__aktualis=True), Q(targy__mintatantervtargy__felev__in=[1, 3, 5]) | Q(targy__mintatantervtargy__oszi_tavaszi=True) | Q(kurzustipus=4)).distinct()
    oktatok = Oktato.objects.filter(pk__in=kurzusok.values_list('oktato', flat=True).distinct())

    args = {}
    args['oktatok'] = oktatok
    return render(request, 'mintatanterv/oktatok_oszi_kurzusai.html', args)


@user_passes_test(in_oktatok_group)
def oktato_kurzusai_osz(request, oktato_id):
    oktato = get_object_or_404(Oktato, pk=oktato_id)
    kurzusok = TargyMunkarend.objects.filter(oktato=oktato).exclude(kurzuskod__icontains='-KV').exclude(nem_indul=True).filter(Q(targy__mintatanterv__aktualis=True), Q(targy__mintatantervtargy__felev__in=[1, 3, 5]) | Q(targy__mintatantervtargy__oszi_tavaszi=True) | Q(kurzustipus=4)).distinct()
    targyak = Targy.objects.filter(pk__in=kurzusok.values_list('targy', flat=True).distinct())

    for targy in targyak:
        targymintatantervek = targy.mintatanterv.filter(aktualis=True)
        targy.mintatantervi_kredit = []
        targy.mintatantervek_felevekkel = []
        targy.mintatantervek_felvetel_tipusaval = []
        for targymintatanterv in targymintatantervek:
            mintatantervtargy = MintatantervTargy.objects.get(mintatanterv=targymintatanterv, targy=targy)
            if mintatantervtargy.kredit:
                string = '%s: %s' % (mintatantervtargy.mintatanterv.kod, mintatantervtargy.kredit)
                targy.mintatantervi_kredit.append(string)
            string2 = '%s: %s. félév' % (mintatantervtargy.mintatanterv.kod, mintatantervtargy.felev)
            targy.mintatantervek_felevekkel.append(string2)
            string3 = '%s: %s' % (mintatantervtargy.mintatanterv.kod, mintatantervtargy.felvetel_tipusa)
            targy.mintatantervek_felvetel_tipusaval.append(string3)

    args = {}
    args['oktato'] = oktato
    args['kurzusok'] = kurzusok
    args['targyak'] = targyak
    return render(request, 'mintatanterv/oktato_oszi_kurzusai.html', args)


@user_passes_test(in_oktatok_group)
def oktatok_kurzusai_tavasz(request):
    kurzusok = TargyMunkarend.objects.exclude(kurzuskod__icontains='-KV').exclude(nem_indul=True).filter(Q(targy__mintatanterv__aktualis=True), Q(targy__mintatantervtargy__felev__in=[2, 4, 6]) | Q(targy__mintatantervtargy__oszi_tavaszi=True) | Q(kurzustipus=4)).distinct()
    oktatok = Oktato.objects.filter(pk__in=kurzusok.values_list('oktato', flat=True).distinct())

    args = {}
    args['oktatok'] = oktatok
    return render(request, 'mintatanterv/oktatok_tavaszi_kurzusai.html', args)


@user_passes_test(in_oktatok_group)
def oktato_kurzusai_tavasz(request, oktato_id):
    oktato = get_object_or_404(Oktato, pk=oktato_id)
    kurzusok = TargyMunkarend.objects.filter(oktato=oktato).exclude(kurzuskod__icontains='-KV').exclude(nem_indul=True).filter(Q(targy__mintatanterv__aktualis=True), Q(targy__mintatantervtargy__felev__in=[2, 4, 6]) | Q(targy__mintatantervtargy__oszi_tavaszi=True) | Q(kurzustipus=4)).distinct()
    targyak = Targy.objects.filter(pk__in=kurzusok.values_list('targy', flat=True).distinct())

    for targy in targyak:
        targymintatantervek = targy.mintatanterv.filter(aktualis=True)
        targy.mintatantervi_kredit = []
        targy.mintatantervek_felevekkel = []
        targy.mintatantervek_felvetel_tipusaval = []
        for targymintatanterv in targymintatantervek:
            mintatantervtargy = MintatantervTargy.objects.get(mintatanterv=targymintatanterv, targy=targy)
            if mintatantervtargy.kredit:
                string = '%s: %s' % (mintatantervtargy.mintatanterv.kod, mintatantervtargy.kredit)
                targy.mintatantervi_kredit.append(string)
            string2 = '%s: %s. félév' % (mintatantervtargy.mintatanterv.kod, mintatantervtargy.felev)
            targy.mintatantervek_felevekkel.append(string2)
            string3 = '%s: %s' % (mintatantervtargy.mintatanterv.kod, mintatantervtargy.felvetel_tipusa)
            targy.mintatantervek_felvetel_tipusaval.append(string3)

    args = {}
    args['oktato'] = oktato
    args['kurzusok'] = kurzusok
    args['targyak'] = targyak
    return render(request, 'mintatanterv/oktato_tavaszi_kurzusai.html', args)


@staff_member_required
def xlsx_oktatok_kurzusai_osz(request):
    kurzusok = TargyMunkarend.objects.exclude(nem_indul=True).filter(Q(targy__mintatanterv__aktualis=True), Q(targy__mintatantervtargy__felev__in=[1, 3, 5]) | Q(targy__mintatantervtargy__oszi_tavaszi=True) | Q(kurzustipus=4)).distinct()

    try:
        felev = Felev.objects.get(aktualis=True)
        felev = felev.felev
    except Felev.DoesNotExist:
        felev = 'Nincs megadva'
    except Felev.MultipleObjectsReturned:
        felev = 'Több is meg van adva'

    output = io.BytesIO()
    book = Workbook(output)
    sheet = book.add_worksheet('oszi_kurzusok')
    sheet.write(0, 0, 'Tárgykód')
    sheet.write(0, 1, 'Félév')
    sheet.write(0, 2, 'Kurzuskód')
    sheet.write(0, 3, 'Maximális létszám')
    sheet.write(0, 4, 'Nyelv')
    sheet.write(0, 5, 'Kurzustípus')
    sheet.write(0, 6, 'Megjegyzés')
    sheet.write(0, 7, 'Heti óraszám')
    sheet.write(0, 8, 'Féléves óraszám')
    sheet.write(0, 9, 'Típusazonosító')
    sheet.write(0, 10, 'Lejelentkezés letiltva')
    sheet.write(0, 11, 'Jelentkezés letiltva')
    sheet.write(0, 12, 'Kurzusfelvételi követelmény')
    sheet.write(0, 13, 'Kurzusfelvételi követelmény leírás')
    sheet.write(0, 14, 'Tagozat')
    sheet.write(0, 15, 'Alkalmazott Neptun kódja')
    sheet.write(0, 16, 'Mintatanterv kódja')
    x = 1
    for kurzus in kurzusok:
        for mintatanterv in kurzus.targy.mintatanterv.filter(aktualis=True):
            switcher = {
                'KJJBA17': 'KJJBA',
                'KJTBA17': 'KJTBA',
                'KJTMA17': 'KJTMA',
                'SZAJBA17': 'SZAJBA17-L' if kurzus.munkarend.nev == 'levelező' else 'SZAJBA17-N',
                'J09': 'JL09' if kurzus.munkarend.nev == 'levelező' else 'JN09',
                'J12': 'JL12' if kurzus.munkarend.nev == 'levelező' else 'JN12',
                'J13': 'JL13' if kurzus.munkarend.nev == 'levelező' else 'JN13',
                'J14': 'JL14' if kurzus.munkarend.nev == 'levelező' else 'JN14',
                'J15': 'JL15' if kurzus.munkarend.nev == 'levelező' else 'JN15',
                'J17': 'JL17' if kurzus.munkarend.nev == 'levelező' else 'JN17',
                'T13': 'TL13' if kurzus.munkarend.nev == 'levelező' else 'TN13',
                'T15': 'TL15' if kurzus.munkarend.nev == 'levelező' else 'TN15',
                'T16': 'TL16' if kurzus.munkarend.nev == 'levelező' else 'TN16',
                'T17': 'TL17' if kurzus.munkarend.nev == 'levelező' else 'TN17',
                'MT14': 'MTN14',
                'MT14J': 'MTN14J',
                'MT14T': 'MTN14T',
                'MT17': 'MTN17',
                'MT17J': 'MTN17J',
                'MT17T': 'MTN17T',
                }
            mintatanterv_kod = switcher.get(mintatanterv.kod, mintatanterv.kod)
            for oktato in kurzus.oktato.all():
                sheet.write(x, 0, kurzus.targy.targykod)
                sheet.write(x, 1, felev)
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
                    if kurzus.kurzustipus.id == 4:
                        sheet.write(x, 9, 'Vizsgakurzus')
                    else:
                        sheet.write(x, 9, 'Normál')
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
    response['Content-Disposition'] = "attachment; filename=oszi_kurzusok_listaja.xlsx"

    return response


@staff_member_required
def xlsx_oktatok_kurzusai_tavasz(request):
    kurzusok = TargyMunkarend.objects.exclude(nem_indul=True).filter(Q(targy__mintatanterv__aktualis=True), Q(targy__mintatantervtargy__felev__in=[2, 4, 6]) | Q(targy__mintatantervtargy__oszi_tavaszi=True) | Q(kurzustipus=4)).distinct()

    try:
        felev = Felev.objects.get(aktualis=True)
        felev = felev.felev
    except Felev.DoesNotExist:
        felev = 'Nincs megadva'
    except Felev.MultipleObjectsReturned:
        felev = 'Több is meg van adva'

    output = io.BytesIO()
    book = Workbook(output)
    sheet = book.add_worksheet('oszi_kurzusok')
    sheet.write(0, 0, 'Tárgykód')
    sheet.write(0, 1, 'Félév')
    sheet.write(0, 2, 'Kurzuskód')
    sheet.write(0, 3, 'Maximális létszám')
    sheet.write(0, 4, 'Nyelv')
    sheet.write(0, 5, 'Kurzustípus')
    sheet.write(0, 6, 'Megjegyzés')
    sheet.write(0, 7, 'Heti óraszám')
    sheet.write(0, 8, 'Féléves óraszám')
    sheet.write(0, 9, 'Típusazonosító')
    sheet.write(0, 10, 'Lejelentkezés letiltva')
    sheet.write(0, 11, 'Jelentkezés letiltva')
    sheet.write(0, 12, 'Kurzusfelvételi követelmény')
    sheet.write(0, 13, 'Kurzusfelvételi követelmény leírás')
    sheet.write(0, 14, 'Tagozat')
    sheet.write(0, 15, 'Alkalmazott Neptun kódja')
    sheet.write(0, 16, 'Mintatanterv kódja')
    x = 1
    for kurzus in kurzusok:
        for mintatanterv in kurzus.targy.mintatanterv.filter(aktualis=True):
            switcher = {
                'KJJBA17': 'KJJBA',
                'KJTBA17': 'KJTBA',
                'KJTMA17': 'KJTMA',
                'SZAJBA17': 'SZAJBA17-L' if kurzus.munkarend.nev == 'levelező' else 'SZAJBA17-N',
                'J09': 'JL09' if kurzus.munkarend.nev == 'levelező' else 'JN09',
                'J12': 'JL12' if kurzus.munkarend.nev == 'levelező' else 'JN12',
                'J13': 'JL13' if kurzus.munkarend.nev == 'levelező' else 'JN13',
                'J14': 'JL14' if kurzus.munkarend.nev == 'levelező' else 'JN14',
                'J15': 'JL15' if kurzus.munkarend.nev == 'levelező' else 'JN15',
                'J17': 'JL17' if kurzus.munkarend.nev == 'levelező' else 'JN17',
                'T13': 'TL13' if kurzus.munkarend.nev == 'levelező' else 'TN13',
                'T15': 'TL15' if kurzus.munkarend.nev == 'levelező' else 'TN15',
                'T16': 'TL16' if kurzus.munkarend.nev == 'levelező' else 'TN16',
                'T17': 'TL17' if kurzus.munkarend.nev == 'levelező' else 'TN17',
                'MT14': 'MTN14',
                'MT14J': 'MTN14J',
                'MT14T': 'MTN14T',
                'MT17': 'MTN17',
                'MT17J': 'MTN17J',
                'MT17T': 'MTN17T',
                }
            mintatanterv_kod = switcher.get(mintatanterv.kod, mintatanterv.kod)
            for oktato in kurzus.oktato.all():
                sheet.write(x, 0, kurzus.targy.targykod)
                sheet.write(x, 1, felev)
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
                    if kurzus.kurzustipus.id == 4:
                        sheet.write(x, 9, 'Vizsgakurzus')
                    else:
                        sheet.write(x, 9, 'Normál')
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
    response['Content-Disposition'] = "attachment; filename=tavaszi_kurzusok_listaja.xlsx"

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

        szakok = list(set(szakok))
        szakok = ', '.join(szakok)
        kurzus.szakok = szakok

    oktatok = list(set(oktatok))
    oktatok = ', '.join(oktatok)
    oktatok1 = list(set(oktatok1))
    oktatok1 = '_'.join(oktatok1)
    kurzuskodok = '_'.join(kurzuskodok)

    try:
        felev = Felev.objects.get(aktualis=True)
        felev = felev.felev
    except Felev.DoesNotExist:
        felev = 'Nincs megadva'
    except Felev.MultipleObjectsReturned:
        felev = 'Több is meg van adva'

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


@user_passes_test(in_oktatok_group)
def jegyzetfelelosok(request):
    jegyzetfelelosok = Oktato.objects.filter(pk__in=TargyOktato.objects.filter(oktato_tipus__nev='Jegyzetfelelős').values_list('oktato', flat=True).distinct())

    args = {}
    args['jegyzetfelelosok'] = jegyzetfelelosok
    return render(request, 'mintatanterv/jegyzetfelelosok.html', args)


@user_passes_test(in_oktatok_group)
def jegyzetfelelos_targyai(request, oktato_id):
    oktato = get_object_or_404(Oktato, pk=oktato_id)
    targyak = Targy.objects.filter(pk__in=TargyOktato.objects.filter(Q(oktato=oktato), Q(oktato_tipus__nev='Jegyzetfelelős')).values_list('targy', flat=True).distinct())

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

