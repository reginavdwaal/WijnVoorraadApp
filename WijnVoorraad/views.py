from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormMixin, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.forms import inlineformset_factory
from django.db.models import Sum, F
from datetime import datetime
from django.utils.html import escape
from django.contrib.auth.models import User

from .models import WijnSoort, DruivenSoort, Deelnemer, Locatie, Vak, Wijn, WijnDruivensoort
from .models import WijnVoorraad, VoorraadMutatie, Ontvangst

from .forms import OntvangstCreateForm, OntvangstUpdateForm, OntvangstMutatieInlineFormset
from .forms import WijnForm, DruivenSoortForm, DeelnemerForm, GebruikerForm, LocatieForm
from .forms import WijnSoortForm

class VoorraadListView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = 'voorraad_list'
    # template_name = 'WijnVoorraad/index.html'

    def get_queryset(self):
        set_session_context (self.request, 'WijnVoorraad:voorraadlist')
        d = get_session_context_deelnemer (self.request)
        l = get_session_context_locatie (self.request)
        voorraad_list = WijnVoorraad.objects.filter(deelnemer__in=d, locatie__in=l).values('wijn', 'wijn__naam', 'wijn__domein', 'wijn__wijnsoort__id', 'wijn__wijnsoort__omschrijving', 'wijn__jaar', 'wijn__land', 'deelnemer','locatie').order_by('wijn', 'deelnemer','locatie').annotate(aantal=Sum('aantal'))
        ws_id = self.kwargs.get('wijnsoort_id_selectie')
        if ws_id is not None:
            voorraad_list = voorraad_list.filter(wijn__wijnsoort__id=ws_id)
        fuzzy = self.kwargs.get('fuzzy_selectie')
        if fuzzy is not None:
            voorraad_list = voorraad_list.filter(wijn__naam__icontains=fuzzy)
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context (context)
        s = WijnSoort.objects.all
        context['wijnsoort_list'] = s
        return context

    def post(self, request, *args, **kwargs):
        ws_id = self.request.POST['wijnsoort_id_selectie']
        fuzzy = self.request.POST['fuzzy_selectie']
        my_kwargs = {}
        if ws_id:
            my_kwargs['wijnsoort_id_selectie'] = ws_id
        if fuzzy:
            my_kwargs['fuzzy_selectie'] = fuzzy
        url = reverse('WijnVoorraad:voorraadlist', kwargs = my_kwargs)
        return HttpResponseRedirect(url)

class VoorraadDetailView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = 'voorraad_list'
    template_name = 'WijnVoorraad/Wijnvoorraad_detail.html'

    def get_queryset(self):
        set_session_context (self.request, 'WijnVoorraad:voorraadlist')
        d = get_session_context_deelnemer (self.request)
        l = get_session_context_locatie (self.request)
        w = self.kwargs['wijn_id']
        voorraad_list = WijnVoorraad.objects.filter(deelnemer__in=d, locatie__in=l, wijn=w)
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context (context)
        context['locaties'] = Locatie.objects.all()  
        context['title'] = 'Voorraad details'  
        return context
    
    def post(self, request, *args, **kwargs):
        v_id = self.request.POST['voorraad_id']
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        if 'Drinken' in self.request.POST:
            WijnVoorraad.drinken(voorraad)
            return HttpResponseRedirect(reverse('WijnVoorraad:voorraadlist'))        
        elif 'Verplaatsen' in self.request.POST:
            v_aantal_verplaatsen = self.request.POST['aantal_verplaatsen']
            v_nieuwe_locatie_id = self.request.POST['nieuwe_locatie_id']
            if v_nieuwe_locatie_id == '-1':
                v_nieuwe_locatie_id = voorraad.locatie.id
            v_nieuwe_locatie = Locatie.objects.get(pk=v_nieuwe_locatie_id)
            v_vakken = Vak.objects.filter(locatie=v_nieuwe_locatie_id)
            if not v_vakken:
                v_nieuwe_vak = None;
                WijnVoorraad.verplaatsen(voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen)
                url = reverse('WijnVoorraad:voorraadlist')
            else:
                url = reverse('WijnVoorraad:verplaatsen', kwargs = dict(voorraad_id = v_id, nieuwe_locatie_id = v_nieuwe_locatie_id, aantal = v_aantal_verplaatsen))
            return HttpResponseRedirect(url)
        else:
            return super().get(request, *args, **kwargs)

class VoorraadOntvangstView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = 'voorraad_list'
    template_name = 'WijnVoorraad/Wijnvoorraad_ontvangst.html'

    def get_queryset(self):
        o = self.kwargs['ontvangst_id']
        voorraad_list = WijnVoorraad.objects.filter(ontvangst=o)
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locaties'] = Locatie.objects.all()  
        context['title'] = 'Voorraad ontvangst'  
        return context
    
    def post(self, request, *args, **kwargs):
        v_id = self.request.POST['voorraad_id']
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        if 'Drinken' in self.request.POST:
            WijnVoorraad.drinken(voorraad)
            return HttpResponseRedirect(reverse('WijnVoorraad:voorraadlist'))        
        elif 'Verplaatsen' in self.request.POST:
            v_aantal_verplaatsen = self.request.POST['aantal_verplaatsen']
            v_nieuwe_locatie_id = self.request.POST['nieuwe_locatie_id']
            if v_nieuwe_locatie_id == '-1':
                v_nieuwe_locatie_id = voorraad.locatie.id
            v_nieuwe_locatie = Locatie.objects.get(pk=v_nieuwe_locatie_id)
            v_vakken = Vak.objects.filter(locatie=v_nieuwe_locatie_id)
            if not v_vakken:
                v_nieuwe_vak = None;
                WijnVoorraad.verplaatsen(voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen)
                url = reverse('WijnVoorraad:voorraadlist')
            else:
                url = reverse('WijnVoorraad:verplaatsen', kwargs = dict(voorraad_id = v_id, nieuwe_locatie_id = v_nieuwe_locatie_id, aantal = v_aantal_verplaatsen))
            return HttpResponseRedirect(url)
        else:
            return super().get(request, *args, **kwargs)

class VoorraadVakkenListView(LoginRequiredMixin, ListView):
    model = Vak
    context_object_name = 'vakken_list'
    template_name = 'WijnVoorraad/voorraadvakken_list.html'

    def get_queryset(self):
        set_session_context (self.request, 'WijnVoorraad:voorraadvakken')
        d = get_session_context_deelnemer (self.request)
        l = get_session_context_locatie (self.request)
        vakken_list = Vak.objects.filter(locatie__in=l).annotate(aantal_gebruikt=Sum('wijnvoorraad__aantal'))
        return vakken_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context (context)
        d = get_session_context_deelnemer (self.request)
        l = get_session_context_locatie (self.request)
        voorraad_list = WijnVoorraad.objects.filter(deelnemer__in=d, locatie__in=l).order_by('vak')
        context['voorraad_list'] = voorraad_list
        context['title'] = 'Vakken'
        return context

class VoorraadVerplaatsen (ListView):
    model = Vak
    template_name = "WijnVoorraad/voorraad_verplaatsen.html"
    success_url = "/WijnVoorraad"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voorraad_id = self.kwargs['voorraad_id']
        voorraad = WijnVoorraad.objects.get(pk=voorraad_id)
        wijn = Wijn.objects.get (pk=voorraad.wijn.id)
        v_nieuwe_locatie_id = self.kwargs['nieuwe_locatie_id']
        vakken_list = Vak.objects.filter(locatie=v_nieuwe_locatie_id).annotate(aantal_gebruikt=Sum('wijnvoorraad__aantal', default=0)).annotate(beschikbaar=F("capaciteit") - F("aantal_gebruikt")).filter(beschikbaar__gt=0).order_by("code")
        context['voorraad'] = voorraad
        context['wijn'] = wijn
        context['aantal_verplaatsen_org'] = self.kwargs['aantal']
        context['nieuwe_locatie'] = Locatie.objects.get(pk=v_nieuwe_locatie_id)
        context['vakken_list'] = vakken_list
        return context

    def post(self, request, *args, **kwargs):
        v_id = self.request.POST['voorraad_id']
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        aantal_vakken = self.request.POST['aantal_vakken']
        try:
            aantal_vakken_int = int(aantal_vakken)
        except:
            aantal_vakken_int = 0
        for i in range(1,aantal_vakken_int):
            v_nieuw_vak_id = self.request.POST['nieuw_vak_id'+str(i)]
            v_aantal_verplaatsen = self.request.POST['aantal_verplaatsen'+str(i)]
            if v_aantal_verplaatsen:
                v_nieuwe_vak = Vak.objects.get(pk=v_nieuw_vak_id)
                v_nieuwe_locatie = v_nieuwe_vak.locatie
                WijnVoorraad.verplaatsen(voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen)

        return HttpResponseRedirect(reverse('WijnVoorraad:voorraadlist'))

class MutatiesUitListView(LoginRequiredMixin, ListView):
    model = VoorraadMutatie
    context_object_name = 'mutatie_list'
    template_name = 'WijnVoorraad/mutatie_uit_list.html'

    def get_queryset(self):
        set_session_context (self.request, 'WijnVoorraad:mutaties_uit')
        d = get_session_context_deelnemer (self.request)
        l = get_session_context_locatie (self.request)
        mutatie_list = VoorraadMutatie.objects.filter(ontvangst__deelnemer__in=d, locatie__in=l, in_uit='U').order_by('-datum')
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context (context)
        context['title'] = 'Uitgaande mutaties'
        return context

class OntvangstListView(LoginRequiredMixin, ListView):
    model = Ontvangst
    context_object_name = 'ontvangsten'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ontvangsten'  
        return context

class OntvangstDetailView(LoginRequiredMixin, DetailView):
    model = Ontvangst
    context_object_name = 'ontvangst'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voorraad_aantal'] = WijnVoorraad.objects.filter(ontvangst=self.object).aggregate(aantal=Sum('aantal'))
        context['mutaties'] = VoorraadMutatie.objects.filter(ontvangst=self.object)  
        context['title'] = 'Ontvangst'  
        return context

class OntvangstCreateView(LoginRequiredMixin, CreateView):
    form_class = OntvangstCreateForm
    model = Ontvangst
    template_name = 'WijnVoorraad/ontvangst_create.html'
    success_url = '/WijnVoorraad'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nieuwe ontvangst'  
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        actie = form.cleaned_data["actie"]
        locatie = form.cleaned_data["locatie"]
        aantal = form.cleaned_data["aantal"]
        mutatie = VoorraadMutatie()
        mutatie.ontvangst = self.object
        mutatie.locatie = locatie
        mutatie.in_uit = 'I'
        mutatie.actie = actie
        mutatie.datum = datetime.now()
        mutatie.aantal = aantal
        mutatie.save()
        if 'SaveAndPlace' in self.request.POST:
            v = WijnVoorraad.objects.filter (ontvangst=self.object)
            url = reverse('WijnVoorraad:verplaatsen', kwargs = dict(voorraad_id = v[0].id, aantal = aantal))
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(self.get_success_url())
   
    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form))

class OntvangstUpdateView(LoginRequiredMixin, UpdateView):
    form_class = OntvangstUpdateForm
    model = Ontvangst
    exclude = ('locatie', 'aantal')
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/ontvangst/{id}'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update ontvangst'  
        return context

class WijnListView(LoginRequiredMixin, ListView):
    model = Wijn
    context_object_name = 'wijn_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Wijnen'  
        return context

class WijnDetailView(LoginRequiredMixin, DetailView):
    model = Wijn
    context_object_name = 'wijn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ontvangst_list'] = Ontvangst.objects.filter(wijn=self.object)  
        context['title'] = 'Wijn'  
        return context

class WijnCreateView(LoginRequiredMixin, CreateView):
    form_class = WijnForm
    model = Wijn
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nieuwe wijn'  
        return context

class WijnUpdateView(LoginRequiredMixin, UpdateView):
    form_class = WijnForm
    model = Wijn
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/wijn/{id}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update wijn'  
        return context

@login_required
def WijnCreatePopupView (request):
    return handlePopAdd(request, WijnForm, 'wijn')

class DeelnemerListView(LoginRequiredMixin, ListView):
    model = Deelnemer
    context_object_name = 'deelnemers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Deelnemers'  
        return context

class DeelnemerDetailView(LoginRequiredMixin, DetailView):
    model = Deelnemer
    context_object_name = 'deelnemer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Deelnemer'
        return context

class DeelnemerCreateView(LoginRequiredMixin, CreateView):
    form_class = DeelnemerForm
    model = Deelnemer
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/deelnemers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nieuwe deelnemer'  
        return context

class DeelnemerUpdateView(LoginRequiredMixin, UpdateView):
    form_class = DeelnemerForm
    model = Deelnemer
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/deelnemer/{id}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update deelnemer'  
        return context

@login_required
def DeelnemerCreatePopupView (request):
    return handlePopAdd(request, DeelnemerForm, 'deelnemer')

@login_required
def DeelnemersCreatePopupView (request):
    return handlePopAdd(request, DeelnemerForm, 'deelnemers')

class DruivenSoortListView(LoginRequiredMixin, ListView):
    model = DruivenSoort
    context_object_name = 'druivensoorten'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Druivensoorten'  
        return context

class DruivenSoortDetailView(LoginRequiredMixin, DetailView):
    model = DruivenSoort
    context_object_name = 'druivensoort'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Druivensoort'  
        return context

class DruivenSoortCreateView(LoginRequiredMixin, CreateView):
    model = DruivenSoort
    fields = '__all__'
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/druivensoorten'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nieuwe druivensoort'  
        return context

class DruivenSoortUpdateView(LoginRequiredMixin, UpdateView):
    model = DruivenSoort
    fields = '__all__'
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/druivensoort/{id}/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update druivensoort'  
        return context
    
@login_required
def DruivenSoortCreatePopupView (request):
    return handlePopAdd(request, DruivenSoortForm, 'druivensoort')

@login_required
def WijnDruivenSoortenCreatePopupView (request):
    return handlePopAdd(request, DruivenSoortForm, 'wijnDruivensoorten')

class WijnSoortListView(LoginRequiredMixin, ListView):
    model = WijnSoort
    context_object_name = 'wijnsoorten'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Wijnsoorten'  
        return context

class WijnSoortDetailView(LoginRequiredMixin, DetailView):
    model = WijnSoort
    context_object_name = 'wijnsoort'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Wijnsoort'  
        return context

class WijnSoortCreateView(LoginRequiredMixin, CreateView):
    model = WijnSoort
    fields = '__all__'
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/wijnsoorten'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nieuwe wijnsoort'  
        return context

class WijnSoortUpdateView(LoginRequiredMixin, UpdateView):
    model = WijnSoort
    fields = '__all__'
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/wijnsoort/{id}/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update wijnsoort'  
        return context
    
@login_required
def WijnSoortCreatePopupView (request):
    return handlePopAdd(request, WijnSoortForm, 'wijnsoort')

class LocatieListView(LoginRequiredMixin, ListView):
    model = Locatie
    context_object_name = 'locaties'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Locaties'  
        return context

class LocatieDetailView(LoginRequiredMixin, DetailView):
    model = Locatie
    context_object_name = 'locatie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vakken'] = Vak.objects.filter(locatie=self.object)  
        context['title'] = 'Locatie'  
        return context

class LocatieCreateView(LoginRequiredMixin, CreateView):
    model = Locatie
    fields = '__all__'
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/locaties'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nieuwe locatie'  
        return context

class LocatieUpdateView(LoginRequiredMixin, UpdateView):
    model = Locatie
    fields = '__all__'
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/locatie/{id}/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update locatie'  
        return context

@login_required
def LocatieCreatePopupView (request):
    return handlePopAdd(request, LocatieForm, 'locatie')

@login_required
def StandaardLocatieCreatePopupView (request):
    return handlePopAdd(request, LocatieForm, 'StandaardLocatie')

class VakDetailView(LoginRequiredMixin, DetailView):
    model = Vak
    context_object_name = 'vak'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Vakken'  
        return context

class VakCreateView(LoginRequiredMixin, CreateView):
    model = Vak
    fields = ["code", "capaciteit"]
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/locatie/{locatie_id}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locatie_id'] = self.kwargs.get('locatie_id')
        context['title'] = 'Nieuw vak'  
        return context

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        self.object.locatie = Locatie.objects.get(pk=self.kwargs.get('locatie_id'))

        super(VakCreateView, self).form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

class VakUpdateView(LoginRequiredMixin, UpdateView):
    model = Vak
    fields = ["code", "capaciteit"]
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/vak/{id}/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update vak'  
        return context

class GebruikerDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'WijnVoorraad/gebruiker_detail.html'
    context_object_name = 'gebruiker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gebruiker'
        return context

class GebruikerUpdateView(LoginRequiredMixin, UpdateView):
    form_class = GebruikerForm
    model = User
    template_name = 'WijnVoorraad/general_create_update.html'
    success_url = '/WijnVoorraad/gebruiker/{id}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update gebruiker'  
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['deelnemers'] = self.request.user.deelnemers.all()
        return initial

    def form_valid(self, form):
        deelnemers = form.cleaned_data['deelnemers']
        self.request.user.deelnemers.clear()
        self.request.user.deelnemers.add(*deelnemers)
        return HttpResponseRedirect(self.get_success_url())
    
def set_session_context (request, return_url):
    dc = request.session.get('deelnemer', None)
    if dc is None:
        du = request.user.deelnemers.all()
        if du.count() >= 1:
            l = du[0].standaardLocatie
            request.session['deelnemer_id'] = du[0].id
            request.session['deelnemer'] = du[0].naam
            request.session['locatie_id'] = l.id
            request.session['locatie'] = l.omschrijving
    request.session['return_url'] = return_url

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

def change_context(request):
    d_id = request.POST['deelnemer_id']
    l_id = request.POST['locatie_id']
    return_url = request.POST['return_url']
    d = Deelnemer.objects.get(pk=d_id)
    l = Locatie.objects.get(pk=l_id)
    request.session['deelnemer_id'] = d_id
    request.session['deelnemer'] = d.naam
    request.session['locatie_id'] = l_id
    request.session['locatie'] = l.omschrijving
    return HttpResponseRedirect(reverse(return_url))

def handlePopAdd(request, addForm, field):
	if request.method == "POST":
		form = addForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				newObject = form.save()
			except form.ValidationError:
				newObject = None
			if newObject:
				return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
					(escape(newObject._get_pk_val()), escape(newObject)))

	else:
		form = addForm()
	pageContext = {'form': form, 'field': field}
	return render(request, "WijnVoorraad/general_popupadd.html", pageContext)



