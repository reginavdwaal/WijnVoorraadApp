from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import WijnSoort, DruivenSoort, Deelnemer, Locatie, Vak, Wijn, WijnDruivensoort, WijnVoorraad, VoorraadMutatie

@login_required
def index(request):
    # if user.is_authenticated:
    #     deelnemers = user.DeelnemerUser.deelnemer.objects.all()
    #     voorraad_list = WijnVoorraad.objects.filer(Deelnemer=deelnemers(1))
    # else:
        # voorraad_list = WijnVoorraad.objects.all()

    voorraad_list = WijnVoorraad.objects.all()

    context = {'voorraad_list': voorraad_list}
    return render(request, 'WijnVoorraad/index.html', context)

def detail(request, voorraad_id):
    voorraad = get_object_or_404(WijnVoorraad, pk=voorraad_id)
    return render(request, 'WijnVoorraad/detail.html', {'voorraad': voorraad})

def drink(request, voorraad_id):
    voorraad = get_object_or_404(WijnVoorraad, pk=voorraad_id)
    return HttpResponseRedirect(reverse('WijnVooraad:detail', args=(voorraad.id,)))
