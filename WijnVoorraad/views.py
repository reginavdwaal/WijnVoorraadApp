"""Main views module"""

from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.db.models import Sum, F
from django.db.models.functions import Lower
from django.contrib import messages

from .models import (
    Locatie,
    Vak,
    Wijn,
)
from .models import WijnVoorraad, VoorraadMutatie, Ontvangst
from .forms import OntvangstCreateForm, OntvangstUpdateForm
from .forms import WijnForm
from .forms import VoorraadFilterForm, MutatieCreateForm, MutatieUpdateForm
from . import wijnvars


class VoorraadListView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = "voorraad_list"
    # template_name = 'WijnVoorraad/index.html'

    def get_queryset(self):
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        voorraad_list = (
            WijnVoorraad.objects.filter(deelnemer=d, locatie=l)
            .group_by("wijn", "ontvangst", "deelnemer", "locatie")
            .distinct()
            .order_by(
                Lower("wijn__domein"), Lower("wijn__naam"), "ontvangst__datumOntvangst"
            )
            .annotate(aantal=Sum("aantal"))
        )

        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            voorraad_list = voorraad_list.filter(wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            voorraad_list = (
                voorraad_list.filter(wijn__naam__icontains=fuzzy_selectie)
                | voorraad_list.filter(wijn__domein__icontains=fuzzy_selectie)
                | voorraad_list.filter(
                    wijn__wijnsoort__omschrijving__icontains=fuzzy_selectie
                )
                | voorraad_list.filter(wijn__jaar__icontains=fuzzy_selectie)
                | voorraad_list.filter(wijn__land__icontains=fuzzy_selectie)
                | voorraad_list.filter(wijn__streek__icontains=fuzzy_selectie)
                | voorraad_list.filter(wijn__classificatie__icontains=fuzzy_selectie)
                | voorraad_list.filter(wijn__opmerking__icontains=fuzzy_selectie)
                | voorraad_list.filter(ontvangst__leverancier__icontains=fuzzy_selectie)
                | voorraad_list.filter(ontvangst__opmerking__icontains=fuzzy_selectie)
                | voorraad_list.filter(
                    wijn__wijnDruivensoorten__omschrijving__icontains=fuzzy_selectie
                )
            )
            voorraad_list = voorraad_list.distinct()
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:voorraadlist"
        )
        return context

    def post(self, request, *args, **kwargs):
        wijnvars.handle_filter_options_post(request)
        url = reverse("WijnVoorraad:voorraadlist")
        return HttpResponseRedirect(url)


class VoorraadFilterView(LoginRequiredMixin, FormView):
    form_class = VoorraadFilterForm
    template_name = "WijnVoorraad/wijnvoorraad_filter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Voorraad filter"
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["deelnemer"] = wijnvars.get_session_deelnemer_id(self.request)
        initial["locatie"] = wijnvars.get_session_locatie_id(self.request)
        initial["wijnsoort"] = wijnvars.get_session_wijnsoort_id(self.request)
        initial["fuzzy_selectie"] = wijnvars.get_session_fuzzy_selectie(self.request)
        return initial

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        d_id = self.request.POST["deelnemer"]
        l_id = self.request.POST["locatie"]
        ws_id = self.request.POST["wijnsoort"]
        fuzzy_selectie = self.request.POST["fuzzy_selectie"]
        wijnvars.set_session_deelnemer(self.request, d_id)
        wijnvars.set_session_locatie(self.request, l_id)
        wijnvars.set_session_wijnsoort_id(self.request, ws_id)
        wijnvars.set_session_fuzzy_selectie(self.request, fuzzy_selectie)
        url = wijnvars.get_session_return_url(self.request)
        return HttpResponseRedirect(reverse(url))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class VoorraadDetailView(LoginRequiredMixin, ListView):
    """Detail view voorraad"""

    model = WijnVoorraad
    context_object_name = "voorraad_list"
    template_name = "WijnVoorraad/wijnvoorraad_detail.html"

    def get_queryset(self):
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        w = self.kwargs["wijn_id"]
        o = self.kwargs["ontvangst_id"]
        voorraad_list = WijnVoorraad.objects.filter(
            deelnemer=d, locatie=l, wijn=w, ontvangst=o
        )
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        w = self.kwargs["wijn_id"]
        context["wijn"] = Wijn.objects.get(pk=w)
        o = self.kwargs["ontvangst_id"]
        context["ontvangst"] = Ontvangst.objects.get(pk=o)
        context["title"] = "Voorraad details"
        return context

    def post(self, request, *args, **kwargs):
        v_id = self.request.POST["voorraad_id"]
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        if "Drinken" in self.request.POST:
            wijn = voorraad.wijn
            WijnVoorraad.drinken(voorraad)
            messages.success(
                request, "Voorraad van %s verminderd met 1" % (wijn.volle_naam,)
            )
            return HttpResponseRedirect(reverse("WijnVoorraad:voorraadlist"))
        elif "Verplaatsen" in self.request.POST:
            url = reverse("WijnVoorraad:verplaatsen", kwargs=dict(pk=v_id))
            return HttpResponseRedirect(url)
        else:
            return super().get(request, *args, **kwargs)


class VoorraadVakkenListView(LoginRequiredMixin, ListView):
    model = Vak
    context_object_name = "vakken_list"
    template_name = "WijnVoorraad/voorraadvakken_list.html"

    def get_queryset(self):
        l = wijnvars.get_session_locatie(self.request)
        vakken_list = (
            Vak.objects.filter(locatie=l)
            .order_by("code")
            .annotate(aantal_gebruikt=Sum("wijnvoorraad__aantal"))
        )
        return vakken_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_default(context, "WijnVoorraad:voorraadvakkenlist")
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        voorraad_list = WijnVoorraad.objects.filter(deelnemer=d, locatie=l).order_by(
            "vak"
        )
        context["locatie"] = l
        context["voorraad_list"] = voorraad_list
        context["title"] = "Vakken"
        return context


class VoorraadVerplaatsen(LoginRequiredMixin, DetailView):
    model = WijnVoorraad
    template_name = "WijnVoorraad/voorraad_verplaatsen.html"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voorraad = self.object
        wijn = Wijn.objects.get(pk=voorraad.wijn.id)
        locatie = Locatie.objects.get(pk=voorraad.locatie.id)
        vak = None
        if voorraad.vak:
            vak = Vak.objects.get(pk=voorraad.vak.id)
        context["voorraad"] = voorraad
        context["wijn"] = wijn
        context["locatie"] = locatie
        context["vak"] = vak
        locatie_list = Locatie.objects.all
        context["locatie_list"] = locatie_list
        context["title"] = "Verplaatsen"
        return context

    def post(self, request, *args, **kwargs):
        v_id = self.request.POST["voorraad_id"]
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        v_nieuwe_locatie_id = self.request.POST["nieuwe_locatie"]
        v_aantal_verplaatsen = self.request.POST["aantal_verplaatsen"]
        if not v_nieuwe_locatie_id:
            # Behouden van dezelfde locatie
            v_nieuwe_locatie = voorraad.locatie
        else:
            v_nieuwe_locatie = Locatie.objects.get(pk=v_nieuwe_locatie_id)

        if "SaveAndPlace" in self.request.POST:
            #
            # Er is gekozen om  vakken te kiezen.
            #
            v_vakken = Vak.objects.filter(locatie=v_nieuwe_locatie)
            if not v_vakken:
                # Als de nieuwe locatie geen vakken heeft, valt er ook niets te kiezen.
                # Als er geen nieuwe locatie is gekozen (maar behouden locatie),
                # dan valt er niets te verplaatsen.
                if v_nieuwe_locatie != voorraad.locatie:
                    # Alsnog direct verplaatsen op de nieuwe locatie
                    v_nieuwe_vak = None
                    wijn = voorraad.wijn
                    WijnVoorraad.verplaatsen(
                        voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
                    )
                    messages.success(
                        request, "Voorraad van %s verplaatst" % (wijn.volle_naam,)
                    )
                url = reverse("WijnVoorraad:voorraadlist")
            else:
                url = reverse(
                    "WijnVoorraad:verplaatsinvakken",
                    kwargs=dict(
                        voorraad_id=voorraad.id,
                        nieuwe_locatie_id=v_nieuwe_locatie.id,
                        aantal=v_aantal_verplaatsen,
                    ),
                )
        else:
            #
            # Er is gekozen om GEEN vakken te kiezen.
            # Als er geen nieuwe locatie is gekozen, valt er niets te verplaatsen
            #
            if v_nieuwe_locatie != voorraad.locatie or voorraad.vak:
                #
                # Wel een nieuwe locatie OF zelfde locatie maar voorraad is van een specifiek vak:
                # Verplaatsen naar de nieuwe locatie zonder vak te kiezen
                #
                v_nieuwe_vak = None
                wijn = voorraad.wijn
                WijnVoorraad.verplaatsen(
                    voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
                )
                messages.success(
                    request, "Voorraad van %s verplaatst" % (wijn.volle_naam,)
                )
            url = reverse("WijnVoorraad:voorraadlist")
        return HttpResponseRedirect(url)


class VoorraadVerplaatsInVakken(LoginRequiredMixin, ListView):
    model = Vak
    template_name = "WijnVoorraad/voorraad_verplaatsinvakken.html"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voorraad_id = self.kwargs["voorraad_id"]
        voorraad = WijnVoorraad.objects.get(pk=voorraad_id)
        wijn = Wijn.objects.get(pk=voorraad.wijn.id)
        v_nieuwe_locatie_id = self.kwargs["nieuwe_locatie_id"]
        vakken_list = (
            Vak.objects.filter(locatie=v_nieuwe_locatie_id)
            .annotate(aantal_gebruikt=Sum("wijnvoorraad__aantal", default=0))
            .annotate(beschikbaar=F("capaciteit") - F("aantal_gebruikt"))
            .filter(beschikbaar__gt=0)
            .order_by("code")
        )
        context["voorraad"] = voorraad
        context["wijn"] = wijn
        context["aantal_verplaatsen_org"] = self.kwargs["aantal"]
        l_nw = Locatie.objects.get(pk=v_nieuwe_locatie_id)
        context["nieuwe_locatie"] = l_nw
        context["vakken_list"] = vakken_list
        if vakken_list.count() > 10:
            context["aantal_kolommen"] = l_nw.aantal_kolommen
        else:
            context["aantal_kolommen"] = 1
        return context

    def post(self, request, *args, **kwargs):
        v_id = self.request.POST["voorraad_id"]
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        wijn = voorraad.wijn
        aantal_vakken = self.request.POST["aantal_vakken"]
        try:
            aantal_vakken_int = int(aantal_vakken)
        except ValueError:
            aantal_vakken_int = 0
        for i in range(1, aantal_vakken_int):
            v_nieuw_vak_id = self.request.POST["nieuw_vak_id" + str(i)]
            v_aantal_verplaatsen = self.request.POST["aantal_verplaatsen" + str(i)]
            if v_aantal_verplaatsen:
                v_nieuwe_vak = Vak.objects.get(pk=v_nieuw_vak_id)
                v_nieuwe_locatie = v_nieuwe_vak.locatie
                WijnVoorraad.verplaatsen(
                    voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
                )

        messages.success(request, "Voorraad van %s verplaatst" % (wijn.volle_naam,))
        return HttpResponseRedirect(reverse("WijnVoorraad:voorraadlist"))


class MutatieListView(LoginRequiredMixin, ListView):
    model = VoorraadMutatie
    context_object_name = "mutatie_list"
    template_name = "WijnVoorraad/mutatie_list.html"

    def get_queryset(self):
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.filter(
            ontvangst__deelnemer=d, locatie=l
        ).order_by("-datum")
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            mutatie_list = mutatie_list.filter(ontvangst__wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            mutatie_list = (
                mutatie_list.filter(omschrijving__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__leverancier__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__opmerking__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__naam__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__domein__icontains=fuzzy_selectie)
                | mutatie_list.filter(
                    ontvangst__wijn__wijnsoort__omschrijving__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(ontvangst__wijn__jaar__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__land__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__streek__icontains=fuzzy_selectie)
                | mutatie_list.filter(
                    ontvangst__wijn__classificatie__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(
                    ontvangst__wijn__opmerking__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(
                    ontvangst__wijn__wijnDruivensoorten__omschrijving__icontains=fuzzy_selectie
                )
            )
            mutatie_list = mutatie_list.distinct()
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_default(context, "WijnVoorraad:mutatielist")
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:mutatielist"
        )
        context["title"] = "Mutaties"
        return context

    def post(self, request, *args, **kwargs):
        wijnvars.handle_filter_options_post(request)
        url = reverse("WijnVoorraad:mutatielist")
        return HttpResponseRedirect(url)


class MutatieUitListView(LoginRequiredMixin, ListView):
    model = VoorraadMutatie
    context_object_name = "mutatie_list"
    template_name = "WijnVoorraad/mutatie_uit_list.html"

    def get_queryset(self):
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.filter(
            ontvangst__deelnemer=d, locatie=l, in_uit="U"
        ).order_by("-datum")
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            mutatie_list = mutatie_list.filter(ontvangst__wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            mutatie_list = (
                mutatie_list.filter(omschrijving__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__leverancier__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__opmerking__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__naam__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__domein__icontains=fuzzy_selectie)
                | mutatie_list.filter(
                    ontvangst__wijn__wijnsoort__omschrijving__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(ontvangst__wijn__jaar__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__land__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__streek__icontains=fuzzy_selectie)
                | mutatie_list.filter(
                    ontvangst__wijn__classificatie__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(
                    ontvangst__wijn__opmerking__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(
                    ontvangst__wijn__wijnDruivensoorten__omschrijving__icontains=fuzzy_selectie
                )
            )
            mutatie_list = mutatie_list.distinct()
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_default(context, "WijnVoorraad:mutatielist_uit")
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:mutatielist_uit"
        )
        context["title"] = "Uitgaande mutaties"
        return context

    def post(self, request, *args, **kwargs):
        wijnvars.handle_filter_options_post(request)
        url = reverse("WijnVoorraad:mutatielist_uit")
        return HttpResponseRedirect(url)


class MutatieInListView(LoginRequiredMixin, ListView):
    model = VoorraadMutatie
    context_object_name = "mutatie_list"
    template_name = "WijnVoorraad/mutatie_in_list.html"

    def get_queryset(self):
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.filter(
            ontvangst__deelnemer=d, locatie=l, in_uit="I"
        ).order_by("-datum")
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            mutatie_list = mutatie_list.filter(ontvangst__wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            mutatie_list = (
                mutatie_list.filter(omschrijving__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__leverancier__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__opmerking__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__naam__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__domein__icontains=fuzzy_selectie)
                | mutatie_list.filter(
                    ontvangst__wijn__wijnsoort__omschrijving__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(ontvangst__wijn__jaar__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__land__icontains=fuzzy_selectie)
                | mutatie_list.filter(ontvangst__wijn__streek__icontains=fuzzy_selectie)
                | mutatie_list.filter(
                    ontvangst__wijn__classificatie__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(
                    ontvangst__wijn__opmerking__icontains=fuzzy_selectie
                )
                | mutatie_list.filter(
                    ontvangst__wijn__wijnDruivensoorten__omschrijving__icontains=fuzzy_selectie
                )
            )
            mutatie_list = mutatie_list.distinct()
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_default(context, "WijnVoorraad:mutatielist_in")
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:mutatielist_in"
        )
        context["title"] = "Inkomende mutaties"
        return context

    def post(self, request, *args, **kwargs):
        wijnvars.handle_filter_options_post(request)
        url = reverse("WijnVoorraad:mutatielist_in")
        return HttpResponseRedirect(url)


class MutatieDetailView(LoginRequiredMixin, DetailView):
    model = VoorraadMutatie
    template_name = "WijnVoorraad/mutatie_detail.html"
    context_object_name = "mutatie"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Mutatie"
        return context

    def post(self, request, *args, **kwargs):
        mutatie_id = self.request.POST["object_id"]
        if mutatie_id:
            mutatie = VoorraadMutatie.objects.get(pk=mutatie_id)
            in_out = mutatie.in_uit
            if "Verwijder" in self.request.POST:
                try:
                    mutatie.delete()
                    messages.success(request, "Mutatie is verwijderd")
                    url = self.request.POST["return_url"]
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse(
                        "WijnVoorraad:mutatiedetail", kwargs=dict(pk=mutatie_id)
                    )
            else:
                url = reverse("WijnVoorraad:mutatiedetail", kwargs=dict(pk=mutatie_id))
            return HttpResponseRedirect(url)


class MutatieCreateView(LoginRequiredMixin, CreateView):
    form_class = MutatieCreateForm
    model = VoorraadMutatie
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:mutatiedetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe mutatie"
        return context

    def get_initial(self):
        initial = super().get_initial()
        ontvangst_id = self.kwargs.get("ontvangst_id")
        if ontvangst_id is not None:
            initial["ontvangst"] = ontvangst_id
        initial["locatie"] = wijnvars.get_session_locatie_id(self.request)
        return initial


class MutatieUpdateView(LoginRequiredMixin, UpdateView):
    form_class = MutatieUpdateForm
    model = VoorraadMutatie
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:mutatiedetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update mutatie"
        return context


class OntvangstListView(LoginRequiredMixin, ListView):
    model = Ontvangst
    context_object_name = "ontvangst_list"

    def get_queryset(self):
        ontvangst_list = Ontvangst.objects.all()
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            ontvangst_list = ontvangst_list.filter(wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            ontvangst_list = (
                ontvangst_list.filter(leverancier__icontains=fuzzy_selectie)
                | ontvangst_list.filter(opmerking__icontains=fuzzy_selectie)
                | ontvangst_list.filter(wijn__naam__icontains=fuzzy_selectie)
                | ontvangst_list.filter(wijn__domein__icontains=fuzzy_selectie)
                | ontvangst_list.filter(
                    wijn__wijnsoort__omschrijving__icontains=fuzzy_selectie
                )
                | ontvangst_list.filter(wijn__jaar__icontains=fuzzy_selectie)
                | ontvangst_list.filter(wijn__land__icontains=fuzzy_selectie)
                | ontvangst_list.filter(wijn__streek__icontains=fuzzy_selectie)
                | ontvangst_list.filter(wijn__classificatie__icontains=fuzzy_selectie)
                | ontvangst_list.filter(wijn__opmerking__icontains=fuzzy_selectie)
                | ontvangst_list.filter(
                    wijn__wijnDruivensoorten__omschrijving__icontains=fuzzy_selectie
                )
            )
            ontvangst_list = ontvangst_list.distinct()
        return ontvangst_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:ontvangstlist"
        )
        context["title"] = "Ontvangsten"
        return context

    def post(self, request, *args, **kwargs):
        wijnvars.handle_filter_options_post(request)
        url = reverse("WijnVoorraad:ontvangstlist")
        return HttpResponseRedirect(url)


class OntvangstDetailView(LoginRequiredMixin, DetailView):
    model = Ontvangst
    context_object_name = "ontvangst"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["voorraad_aantal"] = WijnVoorraad.objects.filter(
            ontvangst=self.object
        ).aggregate(aantal=Sum("aantal"))
        context["mutaties"] = VoorraadMutatie.objects.filter(ontvangst=self.object)
        context["error_message"] = None
        context["title"] = "Ontvangst"
        return context

    def post(self, request, *args, **kwargs):
        o_id = self.request.POST["object_id"]
        if o_id:
            ontvangst = Ontvangst.objects.get(pk=o_id)
            if "VoorraadPlus1" in self.request.POST:
                VoorraadMutatie.voorraad_plus_1(
                    ontvangst, ontvangst.deelnemer.standaardLocatie
                )
                messages.success(
                    request,
                    "Mutatie op standaardlocatie %s toegevoegd"
                    % (ontvangst.deelnemer.standaardLocatie.omschrijving,),
                )
                url = reverse("WijnVoorraad:ontvangstdetail", kwargs=dict(pk=o_id))
            elif "Verwijder" in self.request.POST:
                try:
                    ontvangst.delete()
                    messages.success(request, "Ontvangst is verwijderd")
                    url = reverse("WijnVoorraad:ontvangstlist")
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse("WijnVoorraad:ontvangstdetail", kwargs=dict(pk=o_id))
            elif "Kopieer" in self.request.POST:
                try:
                    nieuwe_ontvangst_id = ontvangst.create_copy()
                    my_kwargs = {}
                    my_kwargs["pk"] = nieuwe_ontvangst_id
                    url = reverse("WijnVoorraad:ontvangst-update", kwargs=my_kwargs)
                except:
                    messages.error(
                        request, "Kopiëren is niet gelukt. Al teveel kopieën?"
                    )
                    url = reverse("WijnVoorraad:wijndetail", kwargs=dict(pk=wijn_id))
            else:
                url = reverse("WijnVoorraad:ontvangstdetail", kwargs=dict(pk=o_id))
            return HttpResponseRedirect(url)
        else:
            return super().get(request, *args, **kwargs)


class OntvangstCreateView(LoginRequiredMixin, CreateView):
    form_class = OntvangstCreateForm
    model = Ontvangst
    template_name = "WijnVoorraad/ontvangst_create.html"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe ontvangst"
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["deelnemer"] = wijnvars.get_session_deelnemer_id(self.request)
        initial["locatie"] = wijnvars.get_session_locatie_id(self.request)
        wijn_id = self.kwargs.get("wijn_id")
        if wijn_id is not None:
            initial["wijn"] = wijn_id
        return initial

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
        mutatie.in_uit = "I"
        mutatie.actie = actie
        mutatie.datum = datetime.now()
        mutatie.aantal = aantal
        mutatie.save()
        if "SaveAndPlace" in self.request.POST:
            v = WijnVoorraad.objects.filter(ontvangst=self.object)
            url = reverse(
                "WijnVoorraad:verplaatsinvakken",
                kwargs=dict(
                    voorraad_id=v[0].id, nieuwe_locatie_id=locatie.id, aantal=aantal
                ),
            )
            return HttpResponseRedirect(url)
        else:
            wijn = self.object.wijn
            messages.success(
                self.request, "Voorraad van %s toegevoegd" % (wijn.volle_naam,)
            )
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class OntvangstUpdateView(LoginRequiredMixin, UpdateView):
    form_class = OntvangstUpdateForm
    model = Ontvangst
    exclude = ("locatie", "aantal")
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:ontvangstdetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update ontvangst"
        return context


class OntvangstVoorraadView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = "voorraad_list"
    template_name = "WijnVoorraad/ontvangst_voorraad.html"

    def get_queryset(self):
        o = self.kwargs["ontvangst_id"]
        voorraad_list = WijnVoorraad.objects.filter(ontvangst=o)
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        o = self.kwargs["ontvangst_id"]
        context["ontvangst"] = Ontvangst.objects.get(pk=o)
        context["title"] = "Ontvangst voorraad"
        return context

    def post(self, request, *args, **kwargs):
        v_id = self.request.POST["voorraad_id"]
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        if "Drinken" in self.request.POST:
            wijn = voorraad.wijn
            WijnVoorraad.drinken(voorraad)
            messages.success(
                request, "Voorraad van %s verminderd met 1" % (wijn.volle_naam,)
            )
            return HttpResponseRedirect(reverse("WijnVoorraad:voorraadlist"))
        elif "Verplaatsen" in self.request.POST:
            url = reverse("WijnVoorraad:verplaatsen", kwargs=dict(pk=v_id))
            return HttpResponseRedirect(url)
        else:
            return super().get(request, *args, **kwargs)


class WijnListView(LoginRequiredMixin, ListView):
    model = Wijn
    context_object_name = "wijn_list"

    def get_queryset(self):
        wijn_list = Wijn.objects.all()
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            wijn_list = wijn_list.filter(wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            wijn_list = (
                wijn_list.filter(naam__icontains=fuzzy_selectie)
                | wijn_list.filter(domein__icontains=fuzzy_selectie)
                | wijn_list.filter(wijnsoort__omschrijving__icontains=fuzzy_selectie)
                | wijn_list.filter(jaar__icontains=fuzzy_selectie)
                | wijn_list.filter(land__icontains=fuzzy_selectie)
                | wijn_list.filter(streek__icontains=fuzzy_selectie)
                | wijn_list.filter(classificatie__icontains=fuzzy_selectie)
                | wijn_list.filter(opmerking__icontains=fuzzy_selectie)
                | wijn_list.filter(
                    wijnDruivensoorten__omschrijving__icontains=fuzzy_selectie
                )
            )
            wijn_list = wijn_list.distinct()
        return wijn_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:wijnlist"
        )
        context["title"] = "Wijnen"
        return context

    def post(self, request, *args, **kwargs):
        wijnvars.handle_filter_options_post(request)
        url = reverse("WijnVoorraad:wijnlist")
        return HttpResponseRedirect(url)


class WijnDetailView(LoginRequiredMixin, DetailView):
    model = Wijn
    context_object_name = "wijn"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["voorraad_aantal"] = WijnVoorraad.objects.filter(
            ontvangst__wijn=self.object
        ).aggregate(aantal=Sum("aantal"))
        context["ontvangst_list"] = Ontvangst.objects.filter(wijn=self.object)
        context["title"] = "Wijn"
        return context

    def post(self, request, *args, **kwargs):
        wijn_id = self.request.POST["object_id"]
        if wijn_id:
            wijn = Wijn.objects.get(pk=wijn_id)
            if "Kopieer" in self.request.POST:
                try:
                    nieuwe_wijn_id = wijn.create_copy()
                    my_kwargs = {}
                    my_kwargs["pk"] = nieuwe_wijn_id
                    url = reverse("WijnVoorraad:wijn-update", kwargs=my_kwargs)
                except:
                    messages.error(
                        request, "Kopiëren is niet gelukt. Al teveel kopieën?"
                    )
                    url = reverse("WijnVoorraad:wijndetail", kwargs=dict(pk=wijn_id))
            elif "Verwijder" in self.request.POST:
                try:
                    wijn.delete()
                    messages.success(request, "Wijn is verwijderd")
                    url = reverse("WijnVoorraad:wijnlist")
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse("WijnVoorraad:wijndetail", kwargs=dict(pk=wijn_id))
            else:
                url = reverse("WijnVoorraad:wijndetail", kwargs=dict(pk=wijn_id))
        else:
            url = reverse("WijnVoorraad:wijnlist")
        return HttpResponseRedirect(url)


class WijnCreateView(LoginRequiredMixin, CreateView):
    form_class = WijnForm
    model = Wijn
    template_name = "WijnVoorraad/general_create_update.html"
    success_url = reverse_lazy("WijnVoorraad:wijnlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe wijn"
        return context


class WijnUpdateView(LoginRequiredMixin, UpdateView):
    form_class = WijnForm
    model = Wijn
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:wijndetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update wijn"
        return context


def change_context(request):
    d_id = request.POST["deelnemer_id"]
    l_id = request.POST["locatie_id"]
    return_url = request.POST["return_url"]
    wijnvars.set_session_deelnemer(request, d_id)
    wijnvars.set_session_locatie(request, l_id)
    return HttpResponseRedirect(reverse(return_url))
