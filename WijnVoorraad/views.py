from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import WijnSoort, DruivenSoort, Deelnemer, Locatie, Vak, Wijn, WijnDruivensoort, WijnVoorraad, VoorraadMutatie

def index(request):
    voorraad_list = WijnVoorraad.objects.all()
    context = {'voorraad_list': voorraad_list}
    return render(request, 'WijnVoorraad/index.html', context)

def detail(request, voorraad_id):
    voorraad = get_object_or_404(WijnVoorraad, pk=voorraad_id)
    return render(request, 'WijnVoorraad/detail.html', {'voorraad': voorraad})

def drink(request, voorraad_id):
    voorraad = get_object_or_404(WijnVoorraad, pk=voorraad_id)
    return HttpResponseRedirect(reverse('WijnVooraad:detail', args=(voorraad.id,)))
