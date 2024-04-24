"""Main views module"""

from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.db.models import Sum, F


from .models import (
    Deelnemer,
    Locatie,
    Vak,
    Wijn,
)
from .models import WijnVoorraad, VoorraadMutatie, Ontvangst
from .forms import OntvangstCreateForm, OntvangstUpdateForm
from .forms import WijnForm
from .forms import VoorraadFilterForm, MutatieForm


class VoorraadListView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = "voorraad_list"
    # template_name = 'WijnVoorraad/index.html'

    def get_queryset(self):
        set_session_context(self.request, "WijnVoorraad:voorraadlist")
        d = get_session_context_deelnemer(self.request)
        l = get_session_context_locatie(self.request)
        voorraad_list = (
            WijnVoorraad.objects.filter(deelnemer=d, locatie=l)
            .group_by("wijn", "ontvangst", "deelnemer", "locatie")
            .distinct()
            .order_by("wijn", "deelnemer", "locatie")
            .annotate(aantal=Sum("aantal"))
        )

        ws_id = self.kwargs.get("wijnsoort_id_selectie")
        if ws_id is not None:
            voorraad_list = voorraad_list.filter(wijn__wijnsoort__id=ws_id)
        fuzzy = self.kwargs.get("fuzzy_selectie")
        if fuzzy is not None:
            if "num" in fuzzy:
                try:
                    num = int(fuzzy[0:-3])
                    fuzzy = str(num)
                except ValueError:
                    pass

            voorraad_list = (
                voorraad_list.filter(wijn__naam__icontains=fuzzy)
                | voorraad_list.filter(wijn__domein__icontains=fuzzy)
                | voorraad_list.filter(wijn__wijnsoort__omschrijving__icontains=fuzzy)
                | voorraad_list.filter(wijn__jaar__icontains=fuzzy)
                | voorraad_list.filter(wijn__land__icontains=fuzzy)
                | voorraad_list.filter(wijn__streek__icontains=fuzzy)
                | voorraad_list.filter(wijn__classificatie__icontains=fuzzy)
                | voorraad_list.filter(wijn__leverancier__icontains=fuzzy)
                | voorraad_list.filter(wijn__opmerking__icontains=fuzzy)
                | voorraad_list.filter(
                    wijn__wijnDruivensoorten__omschrijving__icontains=fuzzy
                )
            )
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context(context)
        fuzzy = self.kwargs.get("fuzzy_selectie")
        if fuzzy is not None:
            if "num" in fuzzy:
                try:
                    num = int(fuzzy[0:-3])
                    context["fuzzy_selectie"] = str(num)
                except ValueError:
                    context["fuzzy_selectie"] = fuzzy
            else:
                context["fuzzy_selectie"] = fuzzy
        return context

    def post(self, request, *args, **kwargs):
        fuzzy = self.request.POST["fuzzy_selectie"]
        my_kwargs = {}
        if fuzzy:
            try:
                int(fuzzy)
                my_kwargs["fuzzy_selectie"] = fuzzy + "num"
            except ValueError:
                my_kwargs["fuzzy_selectie"] = fuzzy

        url = reverse("WijnVoorraad:voorraadlist", kwargs=my_kwargs)
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
        set_session_context(self.request, "WijnVoorraad:voorraadlist_filter")
        initial["deelnemer"] = self.request.session.get("deelnemer_id", None)
        initial["locatie"] = self.request.session.get("locatie_id", None)
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
        d = Deelnemer.objects.get(pk=d_id)
        l = Locatie.objects.get(pk=l_id)
        self.request.session["deelnemer_id"] = d_id
        self.request.session["deelnemer"] = d.naam
        self.request.session["locatie_id"] = l_id
        self.request.session["locatie"] = l.omschrijving
        ws_id = self.request.POST["wijnsoort"]
        fuzzy = self.request.POST["fuzzy_selectie"]
        my_kwargs = {}
        if ws_id:
            my_kwargs["wijnsoort_id_selectie"] = ws_id
        if fuzzy:
            my_kwargs["fuzzy_selectie"] = fuzzy
        url = reverse("WijnVoorraad:voorraadlist", kwargs=my_kwargs)
        return HttpResponseRedirect(url)
        # return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class VoorraadDetailView(LoginRequiredMixin, ListView):
    """Detail view voorraad"""

    model = WijnVoorraad
    context_object_name = "voorraad_list"
    template_name = "WijnVoorraad/wijnvoorraad_detail.html"

    def get_queryset(self):
        set_session_context(self.request, "WijnVoorraad:voorraadlist")
        d = get_session_context_deelnemer(self.request)
        l = get_session_context_locatie(self.request)
        w = self.kwargs["wijn_id"]
        o = self.kwargs["ontvangst_id"]
        voorraad_list = WijnVoorraad.objects.filter(
            deelnemer=d, locatie=l, wijn=w, ontvangst=o
        )
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context(context)
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
            WijnVoorraad.drinken(voorraad)
            return HttpResponseRedirect(reverse("WijnVoorraad:voorraadlist"))
        elif "Verplaatsen" in self.request.POST:
            url = reverse("WijnVoorraad:verplaatsen", kwargs=dict(pk=v_id))
            return HttpResponseRedirect(url)
        else:
            return super().get(request, *args, **kwargs)


class VoorraadOntvangstView(LoginRequiredMixin, ListView):
    model = WijnVoorraad
    context_object_name = "voorraad_list"
    template_name = "WijnVoorraad/Wijnvoorraad_ontvangst.html"

    def get_queryset(self):
        o = self.kwargs["ontvangst_id"]
        voorraad_list = WijnVoorraad.objects.filter(ontvangst=o)
        return voorraad_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        o = self.kwargs["ontvangst_id"]
        context["ontvangst"] = Ontvangst.objects.get(pk=o)
        context["title"] = "Voorraad ontvangst"
        return context

    def post(self, request, *args, **kwargs):
        v_id = self.request.POST["voorraad_id"]
        voorraad = WijnVoorraad.objects.get(pk=v_id)
        if "Drinken" in self.request.POST:
            WijnVoorraad.drinken(voorraad)
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
        set_session_context(self.request, "WijnVoorraad:voorraadvakken")
        l = get_session_context_locatie(self.request)
        vakken_list = (
            Vak.objects.filter(locatie=l).order_by("code")
            .annotate(aantal_gebruikt=Sum("wijnvoorraad__aantal"))
        )
        return vakken_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context(context)
        d = get_session_context_deelnemer(self.request)
        l = get_session_context_locatie(self.request)
        voorraad_list = WijnVoorraad.objects.filter(
            deelnemer=d, locatie=l
        ).order_by("vak")
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
        v_nieuwe_locatie = self.request.POST["nieuwe_locatie"]
        v_aantal_verplaatsen = self.request.POST["aantal_verplaatsen"]
        if not v_nieuwe_locatie:
            # Behouden van dezelfde locatie
            v_nieuwe_locatie = voorraad.locatie

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
                    WijnVoorraad.verplaatsen(
                        voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
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
                WijnVoorraad.verplaatsen(
                    voorraad, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen
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

        return HttpResponseRedirect(reverse("WijnVoorraad:voorraadlist"))


class MutatiesUitListView(LoginRequiredMixin, ListView):
    model = VoorraadMutatie
    context_object_name = "mutatie_list"
    template_name = "WijnVoorraad/mutatie_uit_list.html"

    def get_queryset(self):
        set_session_context(self.request, "WijnVoorraad:mutaties_uit")
        d = get_session_context_deelnemer(self.request)
        l = get_session_context_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.filter(
            ontvangst__deelnemer=d, locatie=l, in_uit="U"
        ).order_by("-datum")
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context(context)
        context["title"] = "Uitgaande mutaties"
        return context


class MutatiesInListView(LoginRequiredMixin, ListView):
    model = VoorraadMutatie
    context_object_name = "mutatie_list"
    template_name = "WijnVoorraad/mutatie_in_list.html"

    def get_queryset(self):
        set_session_context(self.request, "WijnVoorraad:mutaties_in")
        d = get_session_context_deelnemer(self.request)
        l = get_session_context_locatie(self.request)
        mutatie_list = VoorraadMutatie.objects.filter(
            ontvangst__deelnemer=d, locatie=l, in_uit="I"
        ).order_by("-datum")
        return mutatie_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_context(context)
        context["title"] = "Inkomende mutaties"
        return context


class MutatieDetailView(LoginRequiredMixin, DetailView):
    model = VoorraadMutatie
    template_name = "WijnVoorraad/mutatie_detail.html"
    context_object_name = "mutatie"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Mutatie"
        return context


class MutatieUpdateView(LoginRequiredMixin, UpdateView):
    form_class = MutatieForm
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
    context_object_name = "ontvangsten"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ontvangsten"
        return context


class OntvangstDetailView(LoginRequiredMixin, DetailView):
    model = Ontvangst
    context_object_name = "ontvangst"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["voorraad_aantal"] = WijnVoorraad.objects.filter(
            ontvangst=self.object
        ).aggregate(aantal=Sum("aantal"))
        context["mutaties"] = VoorraadMutatie.objects.filter(ontvangst=self.object)
        context["title"] = "Ontvangst"
        return context


class OntvangstCreateView(LoginRequiredMixin, CreateView):
    form_class = OntvangstCreateForm
    model = Ontvangst
    template_name = "WijnVoorraad/ontvangst_create.html"
    success_url = reverse_lazy("WijnVoorraad:voorraadlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe ontvangst"
        return context

    def get_form_kwargs(self):
        kwargs = super(OntvangstCreateView, self).get_form_kwargs()
        set_session_context(self.request, "WijnVoorraad:ontvangst-create")
        my_defaults = {}
        my_defaults["deelnemer_id"] = self.request.session.get("deelnemer_id", None)
        my_defaults["locatie_id"] = self.request.session.get("locatie_id", None)
        kwargs.update({"defaults": my_defaults})
        return kwargs

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


class WijnListView(LoginRequiredMixin, ListView):
    model = Wijn
    context_object_name = "wijn_list"

    def get_queryset(self):
        wijn_list = Wijn.objects.all()
        fuzzy = self.kwargs.get("fuzzy_selectie")
        if fuzzy is not None:
            if "num" in fuzzy:
                try:
                    num = int(fuzzy[0:-3])
                    fuzzy = str(num)
                except ValueError:
                    pass

            wijn_list = (
                wijn_list.filter(naam__icontains=fuzzy)
                | wijn_list.filter(domein__icontains=fuzzy)
                | wijn_list.filter(wijnsoort__omschrijving__icontains=fuzzy)
                | wijn_list.filter(jaar__icontains=fuzzy)
                | wijn_list.filter(land__icontains=fuzzy)
                | wijn_list.filter(streek__icontains=fuzzy)
                | wijn_list.filter(classificatie__icontains=fuzzy)
                | wijn_list.filter(leverancier__icontains=fuzzy)
                | wijn_list.filter(opmerking__icontains=fuzzy)
                | wijn_list.filter(wijnDruivensoorten__omschrijving__icontains=fuzzy)
            )
        return wijn_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fuzzy = self.kwargs.get("fuzzy_selectie")
        if fuzzy is not None:
            if "num" in fuzzy:
                try:
                    num = int(fuzzy[0:-3])
                    context["fuzzy_selectie"] = str(num)
                except ValueError:
                    context["fuzzy_selectie"] = fuzzy
            else:
                context["fuzzy_selectie"] = fuzzy

        context["title"] = "Wijnen"
        return context

    def post(self, request, *args, **kwargs):
        fuzzy = self.request.POST["fuzzy_selectie"]
        my_kwargs = {}
        if fuzzy:
            try:
                int(fuzzy)
                my_kwargs["fuzzy_selectie"] = fuzzy + "num"
            except ValueError:
                my_kwargs["fuzzy_selectie"] = fuzzy

        url = reverse("WijnVoorraad:wijnlist", kwargs=my_kwargs)
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


def set_session_context(request, return_url):
    dc = request.session.get("deelnemer", None)
    if dc is None:
        du = request.user.deelnemers.all()
        if du.count() >= 1:
            l = du[0].standaardLocatie
            request.session["deelnemer_id"] = du[0].id
            request.session["deelnemer"] = du[0].naam
            request.session["locatie_id"] = l.id
            request.session["locatie"] = l.omschrijving
    request.session["return_url"] = return_url


def set_context(context):
    d = Deelnemer.objects.all()
    l = Locatie.objects.all
    context["deelnemer_list"] = d
    context["locatie_list"] = l


def get_session_context_deelnemer(request):
    dc = request.session.get("deelnemer_id", None)
    deelnemer = Deelnemer.objects.get(pk=dc)
    return deelnemer


def get_session_context_locatie(request):
    lc = request.session.get("locatie_id", None)
    locatie = Locatie.objects.get(pk=lc)
    return locatie


def change_context(request):
    d_id = request.POST["deelnemer_id"]
    l_id = request.POST["locatie_id"]
    return_url = request.POST["return_url"]
    d = Deelnemer.objects.get(pk=d_id)
    l = Locatie.objects.get(pk=l_id)
    request.session["deelnemer_id"] = d_id
    request.session["deelnemer"] = d.naam
    request.session["locatie_id"] = l_id
    request.session["locatie"] = l.omschrijving
    return HttpResponseRedirect(reverse(return_url))
