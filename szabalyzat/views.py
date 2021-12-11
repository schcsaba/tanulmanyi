from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from szabalyzat.models import Szabalyzat

@login_required
def szabalyzatok(request):
    args = {}
    if Szabalyzat.objects.all().count() > 0:
        szabalyzatok = Szabalyzat.objects.all()

        args['szabalyzatok'] = szabalyzatok

    else:
        args['visszajelzes'] = 'A szabályzatok még nem érhetők el.'
        args['title'] = 'Türelmét kérjük!'

    return render(request, 'szabalyzat/szabalyzatok.html', args)


@login_required
def szabalyzat_letoltes(request, szabalyzat_id):
    if request.user.is_authenticated and request.user.groups.filter(name='Oktatok').exists():
        if Szabalyzat.objects.filter(id=szabalyzat_id).count() == 1:
            szabalyzat = Szabalyzat.objects.get(id=szabalyzat_id)
            f = open(szabalyzat.szabalyzatfajl.path, 'rb')
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=' + szabalyzat.szabalyzatfajl.name[13:]
            return response
        else:
            return render(request, 'szabalyzat/szabalyzat_nem_letezik.html')
    else:
        if Szabalyzat.objects.filter(id=szabalyzat_id).count() == 1:
            szabalyzat = Szabalyzat.objects.get(id=szabalyzat_id)
            szabalyzatok_hallgatoknak = Szabalyzat.objects.exclude(csak_oktatoknak=True)
            if szabalyzatok_hallgatoknak.filter(id=szabalyzat.id).exists():
                f = open(szabalyzat.szabalyzatfajl.path, 'rb')
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=' + szabalyzat.szabalyzatfajl.name[13:]
                return response
            else:
                return render(request, 'szabalyzat/szabalyzat_nem_hozzaferheto.html')
        else:
            return render(request, 'szabalyzat/szabalyzat_nem_letezik.html')