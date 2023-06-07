from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.db.models import Sum
from datetime import datetime

from .models import WijnSoort, DruivenSoort, Deelnemer, DeelnemerUser, Locatie, Vak, Wijn, WijnDruivensoort
from .models import WijnVoorraad, VoorraadMutatie, Ontvangst

from .forms import OntvangstForm, OntvangstMutatieInlineFormset

def set_session_context (request):
    dc = request.session.get('deelnemer', None)
    if dc is None:
        u = request.user
        du = DeelnemerUser.objects.filter(user=u).values('deelnemer')
        if du.count() == 1:
            d = Deelnemer.objects.filter(pk__in=du)
            l = d[0].standaardLocatie
            request.session['deelnemer_id'] = d[0].id
            request.session['deelnemer'] = d[0].naam
            request.session['locatie_id'] = l.id
            request.session['locatie'] = l.omschrijving

def set_context (context):
        d = Deelnemer.objects.all()
        l = Locatie.objects.all
        context['deelnemer_list'] = d
        context['locatie_list'] = l

def get_session_context_deelnemer (request):
        dc = request.session.get('deelnemer_id', None)
        deelnemer = Deelnemer.objects.filter(pk=dc)
        return deelnemer

def get_session_context_locatie (request):
        lc = request.session.get('locatie_id', None)
        locatie = Locatie.objects.filter(pk=lc)
        return locatie

def detail(request, wijn_id):
    wijn = get_object_or_404(Wijn, pk=wijn_id)
    return render(request, 'WijnVoorraad/detail.html', {'wijn': wijn})

def drink(request, voorraad_id):
    voorraad = get_object_or_404(WijnVoorraad, pk=voorraad_id)
    return HttpResponseRedirect(reverse('WijnVooraad:detail', args=(voorraad.id,)))

def change_context(request):
    d_id = request.POST['deelnemer_id']
    l_id = request.POST['locatie_id']
    d = Deelnemer.objects.get(pk=d_id)
    l = Locatie.objects.get(pk=l_id)
    request.session['deelnemer_id'] = d_id
    request.session['deelnemer'] = d.naam
    request.session['locatie_id'] = l_id
    request.session['locatie'] = l.omschrijving
    # return render(request, 'WijnVoorraad/wijnvoorraad_list.html')
    return HttpResponseRedirect(reverse('WijnVoorraad:voorraadlist'))

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

class OntvangstListView(ListView):
    model = Ontvangst
    context_object_name = 'ontvangsten'

class OntvangstDetailView(DetailView):
    model = Ontvangst
    context_object_name = 'ontvangst'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mutaties'] = VoorraadMutatie.objects.filter(ontvangst=self.object)  
        return context


class VoorraadListView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = 'voorraad_list'
    # template_name = 'WijnVoorraad/index.html'

    def get_queryset(self):
        set_session_context (self.request)
        d = get_session_context_deelnemer (self.request)
        l = get_session_context_locatie (self.request)
        voorraad_list = WijnVoorraad.objects.filter(deelnemer__in=d, locatie__in=l).values('wijn', 'wijn__naam', 'wijn__domein', 'wijn__wijnsoort__omschrijving', 'wijn__jaar', 'wijn__land', 'deelnemer','locatie').order_by('wijn', 'deelnemer','locatie').annotate(aantal=Sum('aantal'))
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context (context)
        return context

class WijnDetailView(DetailView):
    model = Wijn
    context_object_name = 'wijn'

class OntvangstCreateView(LoginRequiredMixin, CreateView):
    form_class = OntvangstForm
    template_name = 'WijnVoorraad/ontvangst_create.html'
    success_url = '/WijnVoorraad'   #  reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mutatie_formset'] = OntvangstMutatieInlineFormset()
        return context

    # def get(self, request, *args, **kwargs):
    #     self.object = None
    #     form_class = self.get_form_class()
    #     return self.render_to_response(
    #         self.get_context_data(form=self.get_form(form_class),
    #                               MutatieFormSet=self.MutatieFormSet()
    #                               ))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        mutatie_formset = OntvangstMutatieInlineFormset(self.request.POST)
        if (form.is_valid() and mutatie_formset.is_valid()):
            return self.form_valid(form, mutatie_formset)
        else:
            return self.form_invalid(form, mutatie_formset)
    
    def form_valid(self, form, mutatie_formset):
        self.object = form.save(commit=False)
        self.object.save()
        mutaties = mutatie_formset.save(commit=False)
        for mutatie in mutaties:
            mutatie.ontvangst = self.object
            mutatie.in_uit = 'I'
            mutatie.actie = 'O'
            mutatie.datum = datetime.now()
            mutatie.save()
        return HttpResponseRedirect(self.get_success_url())
   
    def form_invalid(self, form, mutatie_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  mutatie_formset=mutatie_formset))

