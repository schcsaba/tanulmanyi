from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from faq.models import Kerdes

@login_required
def faq(request):
    args = {}
    args['kerdesek'] = Kerdes.objects.filter(publikalt=True)
    return render(request, 'faq/faq.html', args)
