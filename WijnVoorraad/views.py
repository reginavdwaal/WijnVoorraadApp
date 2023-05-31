from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic import ListView, DetailView

from .models import WijnSoort, DruivenSoort, Deelnemer, DeelnemerUser, Locatie, Vak, Wijn, WijnDruivensoort
from .models import WijnVoorraad, VoorraadMutatie

@login_required
def index(request):
    u = request.user
    du = DeelnemerUser.objects.filter(user=u).values('deelnemer')
    if du.count() == 1:
        d = Deelnemer.objects.filter(pk__in=du)
        l = d[0].standaardLocatie
        request.session['deelnemer'] = d[0].naam
        request.session['locatie'] = l.omschrijving
        voorraad_list = WijnVoorraad.objects.filter(deelnemer__in=d)  
    else:
        d = None
        voorraad_list = WijnVoorraad.objects.all()

    context = {'voorraad_list': voorraad_list}
    context['deelnemer_list'] = d
    request.session['test'] = 'x' 
    return render(request, 'WijnVoorraad/index.html', context)

def detail(request, voorraad_id):
    voorraad = get_object_or_404(WijnVoorraad, pk=voorraad_id)
    return render(request, 'WijnVoorraad/detail.html', {'voorraad': voorraad})

def drink(request, voorraad_id):
    voorraad = get_object_or_404(WijnVoorraad, pk=voorraad_id)
    return HttpResponseRedirect(reverse('WijnVooraad:detail', args=(voorraad.id,)))

class DeelnemerListView(ListView):
    model = Deelnemer
    context_object_name = 'deelnemers'

class DeelnemerDetailView(DetailView):
    model = Deelnemer
    context_object_name = 'deelnemer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voorraad_list'] = WijnVoorraad.objects.filter(deelnemer=self.object)  
        return context