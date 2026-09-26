import os

from django.http import FileResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from szabalyzat.models import Szabalyzat
from tanulmanyi.permissions import is_oktato


@login_required
def szabalyzatok(request):
    args = {}
    szabalyzatok = Szabalyzat.objects.all()
    if szabalyzatok:
        args['szabalyzatok'] = szabalyzatok
    else:
        args['visszajelzes'] = 'A szabályzatok még nem érhetők el.'
        args['title'] = 'Türelmét kérjük!'

    return render(request, 'szabalyzat/szabalyzatok.html', args)


@login_required
def szabalyzat_letoltes(request, szabalyzat_id):
    szabalyzat = Szabalyzat.objects.filter(pk=szabalyzat_id).first()
    if szabalyzat is None:
        return render(request, 'szabalyzat/szabalyzat_nem_letezik.html')
    if szabalyzat.csak_oktatoknak and not is_oktato(request.user):
        return render(request, 'szabalyzat/szabalyzat_nem_hozzaferheto.html')
    fajl = szabalyzat.szabalyzatfajl
    return FileResponse(fajl.open('rb'), as_attachment=True, filename=os.path.basename(fajl.name))
