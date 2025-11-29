"""Main views module"""

import base64
from datetime import datetime
from enum import Enum
import json
from django.utils import timezone

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F, Sum, Count, Case, When
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.core.exceptions import ValidationError, PermissionDenied
from openai import APIError, OpenAI, OpenAIError
from pydantic import BaseModel
from translate import Translator

from . import wijnvars
from .forms import (
    MutatieCreateForm,
    MutatieUpdateForm,
    OntvangstCreateForm,
    OntvangstUpdateForm,
    VoorraadFilterForm,
    WijnForm,
    BestellingCreateForm,
    BestellingUpdateForm,
    BestellingRegelUpdateForm,
)
from .models import (
    AIUsage,
    Deelnemer,
    Locatie,
    Ontvangst,
    Vak,
    VoorraadMutatie,
    Wijn,
    WijnSoort,
    WijnVoorraad,
    Bestelling,
    BestellingRegel,
)
from .services import WijnVoorraadService


def translate_to_dutch(text):
    translator = Translator(to_lang="nl")
    translation = translator.translate(text)
    return translation


# class WineTypeEnum(str, Enum):
#     red = "red"
#     white = "white"
#     rose = "rose"
#     red_port = "red port"
#     white_port = "white port"
#     sparkling = "sparkling"


def generate_wine_type_enum():
    wine_types = WijnSoort.objects.values_list("omschrijving_engels_ai", "omschrijving")

    return Enum(
        "WineTypeEnum",
        {ai_type: human_readable for ai_type, human_readable in wine_types if ai_type},
    )


# Dynamically generate the WineTypeEnum
WineTypeEnum = generate_wine_type_enum()


class WineInfo(BaseModel):
    """structured response model for wine information to be used with OpenAI"""

    wine_domain: str
    year: int
    name: str
    grape_varieties: list[str]
    country: str
    wine_type: str  # Use str for OpenAI compatibility
    region: str
    classification: str
    domain_website_url: str
    description: str


class AdminUserMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff == True


class VoorraadListView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = "voorraad_list"

    def get_queryset(self):
        wijnvars.set_filter_options(
            self.request, True, True, False, False, True, True, True
        )
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        vrd_list = WijnVoorraad.objects.filter(deelnemer=d, locatie=l).order_by(
            "wijn", "ontvangst__datumOntvangst"
        )

        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            vrd_list = vrd_list.filter(wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            vrdnw_list = []
            for vrd in vrd_list:
                if vrd.check_fuzzy_selectie(fuzzy_selectie):
                    vrdnw_list.append(vrd)
            vrd_list = vrdnw_list
        if (
            wijnvars.get_session_sortering(self.request)
            == wijnvars.SorteringEnum.ONTVANGSTWIJN
        ):
            voorraad_list = (
                WijnVoorraad.objects.filter(pk__in=[v.pk for v in vrd_list])
                .group_by("wijn", "ontvangst", "deelnemer", "locatie")
                .order_by("ontvangst__datumOntvangst", "wijn")
                .annotate(aantal=Sum("aantal"))
            )
        elif (
            wijnvars.get_session_sortering(self.request)
            == wijnvars.SorteringEnum.ONTVANGSTDESCWIJN
        ):
            voorraad_list = (
                WijnVoorraad.objects.filter(pk__in=[v.pk for v in vrd_list])
                .group_by("wijn", "ontvangst", "deelnemer", "locatie")
                .order_by("-ontvangst__datumOntvangst", "wijn")
                .annotate(aantal=Sum("aantal"))
            )
        else:
            voorraad_list = (
                WijnVoorraad.objects.filter(pk__in=[v.pk for v in vrd_list])
                .group_by("wijn", "ontvangst", "deelnemer", "locatie")
                .order_by("wijn", "ontvangst__datumOntvangst")
                .annotate(aantal=Sum("aantal"))
            )

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

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["request"] = self.request
        return result

    def get_initial(self):
        initial = super().get_initial()
        if wijnvars.get_bool_deelnemer(self.request):
            initial["deelnemer"] = wijnvars.get_session_deelnemer_id(self.request)
        if wijnvars.get_bool_locatie(self.request):
            initial["locatie"] = wijnvars.get_session_locatie_id(self.request)
        if wijnvars.get_bool_wijnsoort(self.request):
            initial["wijnsoort"] = wijnvars.get_session_wijnsoort_id(self.request)
        if wijnvars.get_bool_fuzzy(self.request):
            initial["fuzzy_selectie"] = wijnvars.get_session_fuzzy_selectie(
                self.request
            )
        if wijnvars.get_bool_sortering(self.request):
            initial["sortering"] = wijnvars.get_session_sortering(self.request)
        return initial

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if wijnvars.get_bool_deelnemer(self.request):
            d_id = self.request.POST["deelnemer"]
            wijnvars.set_session_deelnemer(self.request, d_id)
        if wijnvars.get_bool_locatie(self.request):
            l_id = self.request.POST["locatie"]
            wijnvars.set_session_locatie(self.request, l_id)
        if wijnvars.get_bool_wijnsoort(self.request):
            ws_id = self.request.POST["wijnsoort"]
            wijnvars.set_session_wijnsoort_id(self.request, ws_id)
        if wijnvars.get_bool_fuzzy(self.request):
            fuzzy_selectie = self.request.POST["fuzzy_selectie"]
            wijnvars.set_session_fuzzy_selectie(self.request, fuzzy_selectie)
        if wijnvars.get_bool_sortering(self.request):
            sortering = self.request.POST["sortering"]
            wijnvars.set_session_sortering(self.request, sortering)
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
        l = self.kwargs["locatie_id"]
        w = self.kwargs["wijn_id"]
        o = self.kwargs["ontvangst_id"]
        ontvangst = Ontvangst.objects.get(pk=o)
        d = ontvangst.deelnemer.id
        voorraad_list = WijnVoorraad.objects.filter(
            deelnemer=d, locatie=l, wijn=w, ontvangst=o
        )
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        l = self.kwargs["locatie_id"]
        context["locatie"] = Locatie.objects.get(pk=l)
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
            try:
                voorraad.drinken()
                messages.success(
                    request, "Voorraad van %s verminderd met 1" % (wijn.volle_naam,)
                )
                url = reverse("WijnVoorraad:voorraadlist")
            except ValidationError as e:
                messages.error(request, e.message)
                l = self.kwargs["locatie_id"]
                w = self.kwargs["wijn_id"]
                o = self.kwargs["ontvangst_id"]
                url = reverse(
                    "WijnVoorraad:voorraaddetail",
                    kwargs=dict(locatie_id=l, wijn_id=w, ontvangst_id=o),
                )
            return HttpResponseRedirect(url)
        elif "Afboeken" in self.request.POST:
            o_id = voorraad.ontvangst.id
            url = reverse(
                "WijnVoorraad:mutatie-create",
                kwargs=dict(ontvangst_id=o_id, voorraad_id=v_id),
            )
            return HttpResponseRedirect(url)
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
        wijnvars.set_filter_options(
            self.request, False, True, True, False, True, True, False
        )
        l = wijnvars.get_session_locatie(self.request)
        vakken_list = (
            Vak.objects.filter(locatie=l)
            .order_by("code")
            .annotate(aantal_gebruikt=Sum("wijnvoorraad__aantal"))
        )
        return vakken_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_locatie_list(context)
        l = wijnvars.get_session_locatie(self.request)
        voorraad_list = WijnVoorraad.objects.filter(locatie=l).order_by("vak", "wijn")
        summary_deelnemer_list = (
            WijnVoorraad.objects.filter(locatie=l)
            .group_by("deelnemer")
            .distinct()
            .order_by(Lower("deelnemer__naam"))
            .annotate(aantal=Sum("aantal"))
        )

        summary_wijnsoort_list = (
            WijnVoorraad.objects.filter(locatie=l)
            .group_by("wijn__wijnsoort")
            .distinct()
            .order_by(Lower("wijn__wijnsoort"))
            .annotate(aantal=Sum("aantal"))
        )

        wijnvars.set_context_is_mobile(context, self.request)
        if context["is_mobile"]:
            l.aantal_kolommen = 1
        context["locatie"] = l
        context["voorraad_list"] = voorraad_list
        context["summary_deelnemer_list"] = summary_deelnemer_list
        context["summary_wijnsoort_list"] = summary_wijnsoort_list
        context["title"] = "Voorraad Vakken"
        return context

    def post(self, request, *args, **kwargs):
        l_id = request.POST["locatie_id"]
        wijnvars.set_session_locatie(request, l_id)
        url = reverse("WijnVoorraad:voorraadvakkenlist")
        return HttpResponseRedirect(url)


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
                    voorraad.verplaatsen(
                        v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
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
                voorraad.verplaatsen(
                    v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
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
        for i in range(1, aantal_vakken_int + 1):
            v_nieuw_vak_id = self.request.POST["nieuw_vak_id" + str(i)]
            v_aantal_verplaatsen = self.request.POST["aantal_verplaatsen" + str(i)]
            if v_aantal_verplaatsen:
                v_nieuwe_vak = Vak.objects.get(pk=v_nieuw_vak_id)
                v_nieuwe_locatie = v_nieuwe_vak.locatie
                voorraad.verplaatsen(
                    v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
                )

        messages.success(request, "Voorraad van %s verplaatst" % (wijn.volle_naam,))
        return HttpResponseRedirect(reverse("WijnVoorraad:voorraadlist"))


class MutatieListView(LoginRequiredMixin, ListView):
    model = VoorraadMutatie
    context_object_name = "mutatie_list"
    template_name = "WijnVoorraad/mutatie_list.html"

    def get_queryset(self):
        wijnvars.set_filter_options(
            self.request, True, True, True, True, True, True, False
        )
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.order_by("-datum")
        if d:
            mutatie_list = mutatie_list.filter(ontvangst__deelnemer=d)
        if l:
            mutatie_list = mutatie_list.filter(locatie=l)
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            mutatie_list = mutatie_list.filter(ontvangst__wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            mutnw_list = []
            for mut in mutatie_list:
                if mut.check_fuzzy_selectie(fuzzy_selectie):
                    mutnw_list.append(mut)
            mutatie_list = mutnw_list
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        wijnvars.set_filter_options(
            self.request, True, True, True, True, True, True, False
        )
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.filter(in_uit="U").order_by("-datum")
        if d:
            mutatie_list = mutatie_list.filter(ontvangst__deelnemer=d)
        if l:
            mutatie_list = mutatie_list.filter(locatie=l)
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            mutatie_list = mutatie_list.filter(ontvangst__wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            mutnw_list = []
            for mut in mutatie_list:
                if mut.check_fuzzy_selectie(fuzzy_selectie):
                    mutnw_list.append(mut)
            mutatie_list = mutnw_list
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        wijnvars.set_filter_options(
            self.request, True, True, True, True, True, True, False
        )
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.filter(in_uit="I").order_by("-datum")
        if d:
            mutatie_list = mutatie_list.filter(ontvangst__deelnemer=d)
        if l:
            mutatie_list = mutatie_list.filter(locatie=l)
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            mutatie_list = mutatie_list.filter(ontvangst__wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            mutnw_list = []
            for mut in mutatie_list:
                if mut.check_fuzzy_selectie(fuzzy_selectie):
                    mutnw_list.append(mut)
            mutatie_list = mutnw_list
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

            url = reverse("WijnVoorraad:mutatiedetail", kwargs=dict(pk=mutatie_id))

            if "Verwijder" in self.request.POST:
                try:
                    WijnVoorraad.check_voorraad_wijziging(None, mutatie)
                    mutatie.delete()
                    messages.success(request, "Mutatie is verwijderd")
                    url = self.request.POST["return_url"]
                except ValidationError as e:
                    messages.error(request, e.message)

                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )

            return HttpResponseRedirect(url)


class MutatieCreateView(LoginRequiredMixin, CreateView):
    form_class = MutatieCreateForm
    model = VoorraadMutatie
    template_name = "WijnVoorraad/general_create_update.html"

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["request"] = self.request
        return result

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
        voorraad_id = self.kwargs.get("voorraad_id")
        ontvangst_id = self.kwargs.get("ontvangst_id")
        wijnvars.set_session_extra_var(self.request, "voorraad_id", voorraad_id)
        wijnvars.set_session_extra_var(self.request, "ontvangst_id", ontvangst_id)
        if voorraad_id is not None:
            voorraad = WijnVoorraad.objects.get(pk=voorraad_id)
            initial["voorraad_id"] = voorraad_id
            initial["ontvangst"] = voorraad.ontvangst.id
            initial["locatie"] = voorraad.locatie
            initial["vak"] = voorraad.vak
            initial["in_uit"] = "U"
            initial["actie"] = "A"
            initial["datum"] = datetime.now()
        elif ontvangst_id is not None:
            initial["ontvangst"] = ontvangst_id
            initial["datum"] = datetime.now()
        else:
            initial["locatie"] = wijnvars.get_session_locatie_id(self.request)
            initial["datum"] = datetime.now()
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
    template_name = "WijnVoorraad/ontvangst_list.html"
    context_object_name = "ontvangst_list"

    def get_queryset(self):
        wijnvars.set_filter_options(
            self.request, True, False, True, True, True, True, False
        )
        ontvangst_list = Ontvangst.objects.all()
        d = wijnvars.get_session_deelnemer(self.request)
        if d:
            ontvangst_list = ontvangst_list.filter(deelnemer=d)

        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            ontvangst_list = ontvangst_list.filter(wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            ontvangstnw_list = []
            for ontvangst in ontvangst_list:
                if ontvangst.check_fuzzy_selectie(fuzzy_selectie):
                    ontvangstnw_list.append(ontvangst)
            ontvangst_list = ontvangstnw_list
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
                    url = reverse("WijnVoorraad:ontvangstdetail", kwargs=dict(pk=o_id))
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
            voorraad.drinken()
            messages.success(
                request, "Voorraad van %s verminderd met 1" % (wijn.volle_naam,)
            )
            return HttpResponseRedirect(reverse("WijnVoorraad:voorraadlist"))
        elif "Afboeken" in self.request.POST:
            o_id = voorraad.ontvangst.id
            url = reverse(
                "WijnVoorraad:mutatie-create",
                kwargs=dict(ontvangst_id=o_id, voorraad_id=v_id),
            )
            return HttpResponseRedirect(url)
        elif "Verplaatsen" in self.request.POST:
            url = reverse("WijnVoorraad:verplaatsen", kwargs=dict(pk=v_id))
            return HttpResponseRedirect(url)
        else:
            return super().get(request, *args, **kwargs)


class WijnListView(LoginRequiredMixin, ListView):
    model = Wijn
    template_name = "WijnVoorraad/wijn_list.html"
    context_object_name = "wijn_list"

    def get_queryset(self):
        wijnvars.set_filter_options(
            self.request, False, False, False, False, True, True, False
        )
        wijn_list = Wijn.objects.all()
        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            wijn_list = wijn_list.filter(wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            wijnnw_list = []
            for wijn in wijn_list:
                if wijn.check_fuzzy_selectie(fuzzy_selectie):
                    wijnnw_list.append(wijn)
            wijn_list = wijnnw_list
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


class WijnSearchView(LoginRequiredMixin, DetailView):
    model = Wijn
    context_object_name = "wijn"
    template_name = "WijnVoorraad/wijn_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Wijnen zoeken"
        # wijn = Wijn.objects.get(pk=wijn_id)
        # result=openai.haalfoto(wijn.foto)
        # context["chatgpt"] = self.searchwine()
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
        context["field"] = "wijn"
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
        context["field"] = "wijn"
        return context


class AIview(View):
    """View to handle AI image wine recognition"""

    def searchwine(self, my_image, request):
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        allowed_types = [e.value for e in WineTypeEnum]
        allowed_types_str = ", ".join(allowed_types)
        system_prompt = (
            "You are a wine expert helping to identify wines based on images. "
            f"The allowed wine types are: {allowed_types_str}. "
            "Always use one of these values for the wine type field. "
            "You know the wine type, grape varieties, country, region, and classification of wines. "
            "Search websites like Vivino, Wine-Searcher, and others to find the best information. "
            "If you are sure aboute the domain, find the domain website and if possible validate the information there. "
            "A domain website typically has the domain in its url."
            "From the websites, domain and other also try to find description, taste, and food pairing information. Add references to the websites you used. "
            "You can answer questions like 'What wine is in this picture?' or 'What grape varieties are in this wine?'"
        )

        message = None
        try:
            image_base = base64.b64encode(my_image.read()).decode("utf-8")

            # Use GPT-4 Vision to ask a question about the image
            response = client.beta.chat.completions.parse(
                model="o4-mini",  # Use GPT-4 with Vision support
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Find all information of the wine in this picture?",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base}"
                                },
                            },
                        ],
                    },
                ],
                response_format=WineInfo,
                max_completion_tokens=5000,
            )

        except APIError as e:
            # Handle API error, e.g. retry or log
            message = f"OpenAI API returned an API Error: {e}"

        except OpenAIError as e:
            message = f"AI request failed due to {e}"

        if message:
            return message
        else:
            # Store the response to ai_usage table
            AIUsage.objects.create(
                user=request.user,
                model="gpt-4o-mini",
                response_time=timezone.now(),
                response_content=response.choices[0].message.content,
                response_tokens_used=response.usage.total_tokens,
            )

            # Parse the JSON response
            response_content = response.choices[0].message.content
            response_json = json.loads(response_content)

            try:
                wine_info = WineInfo(**response_json)
            except ValidationError as e:
                print("Validation error:", e)
                # Handle invalid wine_type here

            # if debug print the response
            if settings.DEBUG:
                print("AI response:", response_content)

            # Translate the "country" field
            if "country" in response_json:
                response_json["country"] = translate_to_dutch(response_json["country"])

            # translate description field
            if "description" in response_json:
                response_json["description"] = translate_to_dutch(
                    response_json["description"]
                )

            # Convert the modified JSON back to a string
            translated_response = json.dumps(response_json)
            return translated_response

    def post(self, request, *args, **kwargs):
        image = request.FILES.get("image")  # Ophalen van de afbeelding
        if not image:
            return JsonResponse({"message": "Geen afbeelding ontvangen"}, status=400)

        # Verwerk de afbeelding hier
        print(f"Ontvangen afbeelding: {image.name}")

        response = self.searchwine(image, request)
        print(response)

        # Stuur een antwoord terug
        return JsonResponse({"message": response})


class BestellingCreateView(LoginRequiredMixin, CreateView):
    form_class = BestellingCreateForm
    model = Bestelling
    template_name = "WijnVoorraad/bestelling_create.html"
    success_url = reverse_lazy("WijnVoorraad:bestellinglist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe bestelling"
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["deelnemer"] = wijnvars.get_session_deelnemer_id(self.request)
        return initial

    def post(self, request, *args, **kwargs):
        if "SaveAndDetails" in self.request.POST:
            super().post(request, *args, **kwargs)
            b = self.object
            url = reverse(
                "WijnVoorraad:bestellingregelsselecteren",
                kwargs=dict(bestelling_id=b.id),
            )
            return HttpResponseRedirect(url)
        else:
            return super().post(request, *args, **kwargs)


class BestellingDetailView(LoginRequiredMixin, DetailView):
    model = Bestelling
    context_object_name = "bestelling"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        br = BestellingRegel.objects.filter(bestelling=self.object).order_by(
            "ontvangst__wijn",
            "ontvangst__datumOntvangst",
        )
        vakken = Vak.objects.filter(locatie=self.object.vanLocatie)
        if vakken:
            loc_heeft_vakken = True
        else:
            loc_heeft_vakken = False
        context["loc_heeft_vakken"] = loc_heeft_vakken
        regels = []
        VerzameldeOnverwerkteRegels = False
        AllVerzameld = True
        AllVerwerkt = True
        for regel in br:
            if regel.isVerzameld:
                if regel.verwerkt == "N":
                    VerzameldeOnverwerkteRegels = True
                else:
                    AllVerwerkt = False
            else:
                AllVerzameld = False
            try:
                vrd = WijnVoorraad.objects.get(
                    ontvangst=regel.ontvangst,
                    locatie=regel.bestelling.vanLocatie,
                    vak=regel.vak,
                )
                regel.aantal_vrd = vrd.aantal
                regel.aantal_vrd_rsv = vrd.aantal_rsv
            except WijnVoorraad.DoesNotExist:
                regel.aantal_vrd = 0
                regel.aantal_vrd_rsv = 0
            regels.append(regel)

        br_aggr = br.aggregate(
            tot_aantal=Sum(
                Case(
                    When(
                        aantal_correctie__isnull=False,
                        then=F("aantal_correctie"),
                    ),
                    default=F("aantal"),
                )
            ),
        )

        context["regels"] = regels
        context["tot_aantal"] = br_aggr["tot_aantal"]
        context["VerzameldeOnverwerkteRegels"] = VerzameldeOnverwerkteRegels
        context["AllVerzameld"] = AllVerzameld
        context["AllVerwerkt"] = AllVerwerkt
        context["title"] = "Bestelling"
        return context

    def post(self, request, *args, **kwargs):
        if "VerwijderRegel" in self.request.POST:
            o_id = request.POST.get("bestellingregel_id")
            bestellingregel = BestellingRegel.objects.get(pk=o_id)
            b_id = bestellingregel.bestelling.id
            try:
                bestellingregel.delete()
                messages.success(request, "Bestellingregel is verwijderd")
            except:
                messages.error(
                    request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                )
            url = reverse("WijnVoorraad:bestellingdetail", kwargs=dict(pk=b_id))
            return HttpResponseRedirect(url)
        else:
            o_id = self.request.POST["object_id"]
            if o_id:
                bestelling = Bestelling.objects.get(pk=o_id)
                if "Verwijder" in self.request.POST:
                    try:
                        bestelling.delete()
                        messages.success(request, "Bestelling is verwijderd")
                        url = reverse("WijnVoorraad:bestellinglist")
                    except:
                        messages.error(
                            request,
                            "Verwijderen is niet mogelijk. Gerelateerde gegevens?",
                        )
                        url = reverse(
                            "WijnVoorraad:bestellingdetail", kwargs=dict(pk=o_id)
                        )
                elif "Afboeken" in self.request.POST:
                    try:
                        bestelling.afboeken()
                        messages.success(
                            request, "Verzamelde bestellingregels zijn afgeboekt"
                        )
                    except ValidationError as e:
                        messages.error(request, e.message)
                    url = reverse("WijnVoorraad:bestellingdetail", kwargs=dict(pk=o_id))
                else:
                    url = reverse("WijnVoorraad:bestellingdetail", kwargs=dict(pk=o_id))
                return HttpResponseRedirect(url)
            else:
                return super().get(request, *args, **kwargs)


class BestellingListView(LoginRequiredMixin, ListView):
    model = Bestelling
    template_name = "WijnVoorraad/bestelling_list.html"
    context_object_name = "bestelling_list"

    def get_queryset(self):
        wijnvars.set_filter_options(
            self.request, True, True, True, True, False, False, False
        )
        bestellingen = Bestelling.objects.all()
        d = wijnvars.get_session_deelnemer(self.request)
        l = wijnvars.get_session_locatie(self.request)
        if d:
            bestellingen = bestellingen.filter(deelnemer=d)
        if l:
            bestellingen = bestellingen.filter(vanLocatie=l)

        bestelling_list = []
        for bestelling in bestellingen:
            bestellingregels = BestellingRegel.objects.filter(
                bestelling=bestelling,
            ).aggregate(
                tot_aantal=Sum(
                    Case(
                        When(
                            aantal_correctie__isnull=False,
                            then=F("aantal_correctie"),
                        ),
                        default=F("aantal"),
                    )
                ),
            )

            br_verzameld = BestellingRegel.objects.filter(
                bestelling=bestelling,
                verwerkt="N",
                isVerzameld=True,
            ).aggregate(
                aantal_verzameld=Sum(
                    Case(
                        When(
                            aantal_correctie__isnull=False,
                            then=F("aantal_correctie"),
                        ),
                        default=F("aantal"),
                    )
                ),
            )

            br_verwerkt = (
                BestellingRegel.objects.filter(
                    bestelling=bestelling,
                )
                .exclude(verwerkt="N")
                .aggregate(
                    aantal_verwerkt=Sum(
                        Case(
                            When(
                                aantal_correctie__isnull=False,
                                then=F("aantal_correctie"),
                            ),
                            default=F("aantal"),
                        )
                    ),
                )
            )

            bestelling.tot_aantal = bestellingregels["tot_aantal"] or 0
            bestelling.aantal_verzameld = br_verzameld["aantal_verzameld"]
            bestelling.aantal_verwerkt = br_verwerkt["aantal_verwerkt"]
            bestelling_list.append(bestelling)

        return bestelling_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:bestellinglist"
        )
        context["title"] = "Bestellingen"
        return context

    def post(self, request, *args, **kwargs):
        wijnvars.handle_filter_options_post(request)
        url = reverse("WijnVoorraad:bestellinglist")
        return HttpResponseRedirect(url)


class BestellingUpdateView(LoginRequiredMixin, UpdateView):
    form_class = BestellingUpdateForm
    model = Bestelling
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:bestellingdetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update bestelling"
        return context


class BestellingRegelsSelecteren(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    template_name = "WijnVoorraad/bestellingregels_selecteren.html"
    context_object_name = "bestel_list"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_queryset(self):
        wijnvars.set_filter_options(
            self.request, False, False, False, False, True, True, False
        )
        b_id = self.kwargs["bestelling_id"]
        b = Bestelling.objects.get(pk=b_id)
        d = Deelnemer.objects.get(pk=b.deelnemer.id)
        l = Locatie.objects.get(pk=b.vanLocatie.id)
        voorraad_list = WijnVoorraad.objects.filter(deelnemer=d, locatie=l).order_by(
            "wijn", "ontvangst__datumOntvangst"
        )

        ws_id = wijnvars.get_session_wijnsoort_id(self.request)
        if ws_id:
            voorraad_list = voorraad_list.filter(wijn__wijnsoort__id=ws_id)

        fuzzy_selectie = wijnvars.get_session_fuzzy_selectie(self.request)
        if fuzzy_selectie:
            vrdnw_list = []
            for vrd in voorraad_list:
                if vrd.check_fuzzy_selectie(fuzzy_selectie):
                    vrdnw_list.append(vrd)
            voorraad_list = vrdnw_list
        bestel_list = []
        for vrd in voorraad_list:
            try:
                br = BestellingRegel.objects.get(
                    bestelling=b, ontvangst=vrd.ontvangst, vak=vrd.vak
                )
                vrd.bestellingregel_id = br.id
                vrd.aantal_bestellen = br.aantal
            except:
                vrd.bestellingregel_id = ""
                vrd.aantal_bestellen = ""
            bestel_list.append(vrd)
        return bestel_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:bestellingregelsselecteren"
        )
        bestelling_id = self.kwargs["bestelling_id"]
        bestelling = Bestelling.objects.get(pk=bestelling_id)
        context["bestelling"] = bestelling
        context["title"] = "Bestelling selecteren"
        return context

    def post(self, request, *args, **kwargs):
        if "FilterPost" in request.POST:
            wijnvars.handle_filter_options_post(request)
            b_id = self.kwargs["bestelling_id"]
            url = reverse(
                "WijnVoorraad:bestellingregelsselecteren",
                kwargs=dict(bestelling_id=b_id),
            )
        else:
            b_id = request.POST.get("bestelling_id")
            bestelling = Bestelling.objects.get(pk=b_id)
            aantal_vrd = request.POST["aantal_vrd"]
            try:
                aantal_vrd_int = int(aantal_vrd)
            except ValueError:
                aantal_vrd_int = 0
            aantal_regels = 0
            for i in range(1, aantal_vrd_int + 1):
                v_id = request.POST["voorraad_id" + str(i)]
                v_aantal_bestellen = request.POST["aantal_bestellen" + str(i)]
                br_id = request.POST.get("bestellingregel_id" + str(i))
                if br_id:
                    br = BestellingRegel.objects.get(pk=br_id)
                    if v_aantal_bestellen:
                        if br.aantal != int(v_aantal_bestellen):
                            br.aantal = v_aantal_bestellen
                            br.save()
                            aantal_regels += 1
                    else:
                        br.delete()
                        aantal_regels += 1
                elif v_aantal_bestellen:
                    voorraad = WijnVoorraad.objects.get(pk=v_id)
                    v_nieuwe_bestelregel = BestellingRegel()
                    v_nieuwe_bestelregel.bestelling = bestelling
                    v_nieuwe_bestelregel.ontvangst = voorraad.ontvangst
                    v_nieuwe_bestelregel.vak = voorraad.vak
                    v_nieuwe_bestelregel.aantal = v_aantal_bestellen
                    v_nieuwe_bestelregel.opmerking = ""
                    v_nieuwe_bestelregel.save()
                    aantal_regels += 1
            messages.success(request, "%s bestelregel(s) verwerkt" % (aantal_regels,))
            url = reverse("WijnVoorraad:bestellingdetail", kwargs=dict(pk=b_id))
        return HttpResponseRedirect(url)


class BestellingRegelUpdateView(LoginRequiredMixin, UpdateView):
    form_class = BestellingRegelUpdateForm
    model = BestellingRegel
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:bestellingdetail",
            kwargs={"pk": self.object.bestelling.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update bestellingregel"
        return context


class BestellingenVerzamelen(LoginRequiredMixin, ListView):
    model = Bestelling
    template_name = "WijnVoorraad/bestellingen_verzamelen.html"
    context_object_name = "bestelling_list"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_queryset(self):
        wijnvars.set_filter_options(
            self.request, False, True, True, False, False, False, False
        )
        l = wijnvars.get_session_locatie(self.request)
        bestellingen = Bestelling.objects.filter(
            vanLocatie=l, datumAfgesloten__isnull=True
        )
        bestelling_list = []
        for bestelling in bestellingen:
            bestellingregels = BestellingRegel.objects.filter(
                bestelling=bestelling,
            ).aggregate(
                tot_aantal=Sum(
                    Case(
                        When(
                            aantal_correctie__isnull=False,
                            then=F("aantal_correctie"),
                        ),
                        default=F("aantal"),
                    )
                ),
            )

            br_verzameld = BestellingRegel.objects.filter(
                bestelling=bestelling,
                verwerkt="N",
                isVerzameld=True,
            ).aggregate(
                aantal_verzameld=Sum(
                    Case(
                        When(
                            aantal_correctie__isnull=False,
                            then=F("aantal_correctie"),
                        ),
                        default=F("aantal"),
                    )
                ),
            )

            br_verwerkt = (
                BestellingRegel.objects.filter(
                    bestelling=bestelling,
                )
                .exclude(verwerkt="N")
                .aggregate(
                    aantal_verwerkt=Sum(
                        Case(
                            When(
                                aantal_correctie__isnull=False,
                                then=F("aantal_correctie"),
                            ),
                            default=F("aantal"),
                        )
                    ),
                )
            )

            bestelling.tot_aantal = bestellingregels["tot_aantal"] or 0
            bestelling.aantal_verzameld = br_verzameld["aantal_verzameld"]
            bestelling.aantal_verwerkt = br_verwerkt["aantal_verwerkt"]
            bestelling_list.append(bestelling)

        return bestelling_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wijnvars.set_context_filter_options(
            context, self.request, "WijnVoorraad:bestellingenverzamelen"
        )
        wijnvars.set_context_locatie_list(context)
        l = wijnvars.get_session_locatie(self.request)
        vakken = Vak.objects.filter(locatie=l)
        if vakken:
            loc_heeft_vakken = True
        else:
            loc_heeft_vakken = False
        context["locatie"] = l
        context["loc_heeft_vakken"] = loc_heeft_vakken
        br = BestellingRegel.objects.filter(
            bestelling__vanLocatie=l, bestelling__datumAfgesloten__isnull=True
        ).order_by(
            "ontvangst__wijn",
            "ontvangst__datumOntvangst",
        )

        bestelregel_list = []
        for regel in br:
            try:
                vrd = WijnVoorraad.objects.get(
                    ontvangst=regel.ontvangst,
                    locatie=regel.bestelling.vanLocatie,
                    vak=regel.vak,
                )
                regel.aantal_vrd = vrd.aantal
            except WijnVoorraad.DoesNotExist:
                regel.aantal_vrd = 0
            bestelregel_list.append(regel)

        br_aggr = br.aggregate(
            tot_aantal=Sum(
                Case(
                    When(
                        aantal_correctie__isnull=False,
                        then=F("aantal_correctie"),
                    ),
                    default=F("aantal"),
                )
            ),
        )
        context["loc_heeft_vakken"] = loc_heeft_vakken
        context["bestelregel_list"] = bestelregel_list
        context["tot_aantal"] = br_aggr["tot_aantal"]
        context["title"] = "Bestellingen verzamelen"
        return context

    def post(self, request, *args, **kwargs):
        if "FilterPost" in request.POST:
            l_id = request.POST["locatie_id"]
            wijnvars.set_session_locatie(request, l_id)
            wijnvars.handle_filter_options_post(request)
        else:
            aantal_rgls = request.POST["aantal_rgls"]
            try:
                aantal_rgls_int = int(aantal_rgls)
            except ValueError:
                aantal_rgls_int = 0
            for i in range(1, aantal_rgls_int + 1):
                br_id = request.POST["bestellingregel_id" + str(i)]
                br_isVerzameld = request.POST.get("isVerzameld" + str(i))
                br_aantal_correctie = request.POST.get("aantal_correctie" + str(i))
                br_opmerking = request.POST.get("opmerking" + str(i))
                if br_id:
                    br = BestellingRegel.objects.get(pk=br_id)
                    br.isVerzameld = br_isVerzameld == "True"
                    if br_aantal_correctie:
                        br.aantal_correctie = int(br_aantal_correctie)
                    else:
                        br.aantal_correctie = None
                    br.opmerking = br_opmerking
                    try:
                        br.save()
                    except ValidationError as e:
                        messages.error(request, e.message)

        url = reverse("WijnVoorraad:bestellingenverzamelen")
        return HttpResponseRedirect(url)


class BestellingVerzamelenDetail(LoginRequiredMixin, DetailView):
    model = Bestelling
    template_name = "WijnVoorraad/bestelling_verzamelen_detail.html"
    context_object_name = "bestelling"
    success_url = reverse_lazy("WijnVoorraad:bestellingenverzamelen")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        l = wijnvars.get_session_locatie(self.request)
        vakken = Vak.objects.filter(locatie=l)
        if vakken:
            loc_heeft_vakken = True
        else:
            loc_heeft_vakken = False

        br = BestellingRegel.objects.filter(
            bestelling=self.object,
        ).order_by(
            "ontvangst__wijn",
            "ontvangst__datumOntvangst",
        )

        bestelregel_list = []
        for regel in br:
            try:
                vrd = WijnVoorraad.objects.get(
                    ontvangst=regel.ontvangst,
                    locatie=regel.bestelling.vanLocatie,
                    vak=regel.vak,
                )
                regel.aantal_vrd = vrd.aantal
            except WijnVoorraad.DoesNotExist:
                regel.aantal_vrd = 0
            bestelregel_list.append(regel)

        br_aggr = br.aggregate(
            tot_aantal=Sum(
                Case(
                    When(
                        aantal_correctie__isnull=False,
                        then=F("aantal_correctie"),
                    ),
                    default=F("aantal"),
                )
            ),
        )
        context["loc_heeft_vakken"] = loc_heeft_vakken
        context["bestelregel_list"] = bestelregel_list
        context["tot_aantal"] = br_aggr["tot_aantal"]
        context["title"] = "Bestelling verzamelen"
        return context

    def post(self, request, *args, **kwargs):
        aantal_rgls = request.POST["aantal_rgls"]
        try:
            aantal_rgls_int = int(aantal_rgls)
        except ValueError:
            aantal_rgls_int = 0
        for i in range(1, aantal_rgls_int + 1):
            br_id = request.POST["bestellingregel_id" + str(i)]
            br_isVerzameld = request.POST.get("isVerzameld" + str(i))
            br_aantal_correctie = request.POST.get("aantal_correctie" + str(i))
            br_opmerking = request.POST.get("opmerking" + str(i))
            if br_id:
                br = BestellingRegel.objects.get(pk=br_id)
                br.isVerzameld = br_isVerzameld == "True"
                if br_aantal_correctie:
                    br.aantal_correctie = int(br_aantal_correctie)
                else:
                    br.aantal_correctie = None
                br.opmerking = br_opmerking
                try:
                    br.save()
                except ValidationError as e:
                    messages.error(request, e.message)
        if messages.get_messages(request):
            url = reverse("WijnVoorraad:bestellingverzamelendetail")
        else:
            url = reverse("WijnVoorraad:bestellingenverzamelen")
        return HttpResponseRedirect(url)


class BestellingRegelVerplaatsen(LoginRequiredMixin, DetailView):
    model = BestellingRegel
    template_name = "WijnVoorraad/bestellingregel_verplaatsen.html"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        regel = self.object
        wijn = Wijn.objects.get(pk=regel.ontvangst.wijn.id)
        locatie = Locatie.objects.get(pk=regel.bestelling.vanLocatie.id)
        vak = None
        if regel.vak:
            vak = Vak.objects.get(pk=regel.vak.id)
        context["bestellingregel"] = regel
        context["wijn"] = wijn
        context["locatie"] = locatie
        context["vak"] = vak
        locatie_list = Locatie.objects.all
        context["locatie_list"] = locatie_list
        context["title"] = "Bestellingregel verplaatsen"
        return context

    def post(self, request, *args, **kwargs):
        br_id = self.request.POST["bestellingregel_id"]
        regel = BestellingRegel.objects.get(pk=br_id)
        v_nieuwe_locatie_id = self.request.POST["nieuwe_locatie"]
        if regel.aantal_correctie is not None:
            v_aantal_verplaatsen = regel.aantal_correctie
        else:
            v_aantal_verplaatsen = regel.aantal

        if not v_nieuwe_locatie_id:
            # Behouden van dezelfde locatie
            v_nieuwe_locatie = regel.bestelling.vanLocatie
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
                if v_nieuwe_locatie != regel.bestelling.vanLocatie:
                    # Alsnog direct verplaatsen op de nieuwe locatie
                    v_nieuwe_vak = None
                    regel.verplaatsen(
                        v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
                    )
                    messages.success(
                        request,
                        "Bestelregel %s verplaatst"
                        % (regel.ontvangst.wijn.volle_naam,),
                    )
                url = reverse(
                    "WijnVoorraad:bestellingdetail", kwargs=dict(pk=regel.bestelling.id)
                )
            else:
                url = reverse(
                    "WijnVoorraad:bestellingregelverplaatsinvakken",
                    kwargs=dict(
                        bestellingregel_id=regel.id,
                        nieuwe_locatie_id=v_nieuwe_locatie.id,
                        aantal=v_aantal_verplaatsen,
                    ),
                )
        else:
            #
            # Er is gekozen om GEEN vakken te kiezen.
            # Als er geen nieuwe locatie is gekozen, valt er niets te verplaatsen
            #
            if v_nieuwe_locatie != regel.bestelling.vanLocatie or regel.vak:
                #
                # Wel een nieuwe locatie OF zelfde locatie maar voorraad is van een specifiek vak:
                # Verplaatsen naar de nieuwe locatie zonder vak te kiezen
                #
                v_nieuwe_vak = None
                regel.verplaatsen(v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen)
                messages.success(
                    request,
                    "Bestelregel %s verplaatst" % (regel.ontvangst.wijn.volle_naam,),
                )
                url = reverse(
                    "WijnVoorraad:bestellingdetail", kwargs=dict(pk=regel.bestelling.id)
                )
        return HttpResponseRedirect(url)


class BestellingregelVerplaatsInVakken(LoginRequiredMixin, ListView):
    model = Vak
    template_name = "WijnVoorraad/bestellingregel_verplaatsinvakken.html"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        br_id = self.kwargs["bestellingregel_id"]
        regel = BestellingRegel.objects.get(pk=br_id)
        wijn = Wijn.objects.get(pk=regel.ontvangst.wijn.id)
        v_nieuwe_locatie_id = self.kwargs["nieuwe_locatie_id"]
        vakken_list = (
            Vak.objects.filter(locatie=v_nieuwe_locatie_id)
            .annotate(aantal_gebruikt=Sum("wijnvoorraad__aantal", default=0))
            .annotate(beschikbaar=F("capaciteit") - F("aantal_gebruikt"))
            .filter(beschikbaar__gt=0)
            .order_by("code")
        )
        context["bestellingregel"] = regel
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
        br_id = self.request.POST["bestellingregel_id"]
        regel = BestellingRegel.objects.get(pk=br_id)
        aantal_vakken = self.request.POST["aantal_vakken"]
        try:
            aantal_vakken_int = int(aantal_vakken)
        except ValueError:
            aantal_vakken_int = 0
        for i in range(1, aantal_vakken_int + 1):
            v_nieuw_vak_id = self.request.POST["nieuw_vak_id" + str(i)]
            v_aantal_verplaatsen = self.request.POST["aantal_verplaatsen" + str(i)]
            if v_aantal_verplaatsen:
                v_nieuwe_vak = Vak.objects.get(pk=v_nieuw_vak_id)
                v_nieuwe_locatie = v_nieuwe_vak.locatie
                # bijwerken van de verwerktstatus van de regel pas als alle verplaatsingen klaar zijn
                bijwerken = False
                regel.verplaatsen(
                    v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen, bijwerken
                )
        regel.verwerkt = "V"
        regel.save()

        messages.success(
            request,
            "Bestellingregel %s verplaatst" % (regel.ontvangst.wijn.volle_naam,),
        )
        url = reverse(
            "WijnVoorraad:bestellingdetail", kwargs=dict(pk=regel.bestelling.id)
        )
        return HttpResponseRedirect(url)


class VoorraadControleren(AdminUserMixin, ListView):
    model = Locatie
    context_object_name = "locatie_list"
    template_name = "WijnVoorraad/voorraad_controleren.html"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")
    raise_exception = True

    def get_queryset(self):
        locatie_list = WijnVoorraadService.ControleerAlleLocaties()
        return locatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ontvangst_list = WijnVoorraadService.ControleerAlleOntvangsten()
        context["ontvangst_list"] = ontvangst_list
        context["title"] = "Voorraad controleren"
        return context

    def post(self, request, *args, **kwargs):
        # locatie_id = self.request.POST.get("locatie_id")
        ontvangst_id = self.request.POST.get("ontvangst_id")
        if "BijwerkenVrdOntvangst" in self.request.POST:
            ontvangst = Ontvangst.objects.get(pk=ontvangst_id)
            WijnVoorraadService.BijwerkenVrdOntvangst(ontvangst)
        url = reverse("WijnVoorraad:voorraadcontroleren")
        return HttpResponseRedirect(url)
