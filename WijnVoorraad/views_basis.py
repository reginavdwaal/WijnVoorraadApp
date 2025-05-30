"""Views voor de stam gegevens zoals Gebruiker, Wijn etc"""

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages

from WijnVoorraad.forms import DeelnemerForm, GebruikerForm, VakForm
from WijnVoorraad.models import Deelnemer, DruivenSoort, Locatie, Vak, WijnSoort


class GebruikerDetailView(LoginRequiredMixin, DetailView):
    """Details view class voor Gebruiker"""

    model = User
    template_name = "WijnVoorraad/gebruiker_detail.html"
    context_object_name = "gebruiker"

    def get_context_data(self, **kwargs):
        """Adding Gebruiker as title to context"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Gebruiker"
        return context


class GebruikerUpdateView(LoginRequiredMixin, UpdateView):
    """Update view class gebruiker"""

    form_class = GebruikerForm
    model = User
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        """
        Functie overschreven om gebruik te kunnen maken van path op basis van naam
        en meegeven van id.
        """
        return reverse_lazy(
            "WijnVoorraad:gebruikerdetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        """Voegt title toe aan context"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Update gebruiker"
        return context

    def get_initial(self):
        """Voegt deelnemers toe aan 'initial'"""
        initial = super().get_initial()
        initial["deelnemers"] = self.request.user.deelnemers.all()
        return initial

    def form_valid(self, form):
        """Gebruik validatie method om deelnemers als object aan request toe te voegen"""
        deelnemers = form.cleaned_data["deelnemers"]
        self.request.user.deelnemers.clear()
        self.request.user.deelnemers.add(*deelnemers)
        return super().form_valid(form)


class VakUpdateView(LoginRequiredMixin, UpdateView):
    """Standaard view class voor bijwerken Vak"""

    model = Vak
    fields = ["code", "capaciteit"]
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:vakdetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update vak"
        return context


class VakCreateView(LoginRequiredMixin, CreateView):
    """Standaard view class voor vak aanmaken"""

    model = Vak
    form_class = VakForm
    # fields = ["code", "capaciteit"]
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:

        return reverse_lazy(
            "WijnVoorraad:locatiedetail",
            kwargs={"pk": self.object.locatie_id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["locatie_id"] = self.kwargs.get("locatie_id")
        context["title"] = "Nieuw vak"
        return context

    def get_initial(self):
        """Voegt locatie id toe aan initial data"""
        initial = super().get_initial()
        initial["locatie"] = self.kwargs.get("locatie_id")

        return initial


class VakDetailView(LoginRequiredMixin, DetailView):
    """Standaard view class voor vak aanmaken"""

    model = Vak
    context_object_name = "vak"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Vakken"
        return context

    def post(self, request, *args, **kwargs):
        vak_id = self.request.POST["object_id"]
        if vak_id:
            vak = Vak.objects.get(pk=vak_id)
            locatie_id = vak.locatie.id
            if "Verwijder" in self.request.POST:
                try:
                    vak.delete()
                    messages.success(request, "Vak is verwijderd")
                    url = reverse(
                        "WijnVoorraad:locatiedetail", kwargs=dict(pk=locatie_id)
                    )
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse("WijnVoorraad:vakdetail", kwargs=dict(pk=vak_id))
            else:
                url = reverse("WijnVoorraad:vakdetail", kwargs=dict(pk=vak_id))
        else:
            url = reverse("WijnVoorraad:locatielist")
        return HttpResponseRedirect(url)


class LocatieUpdateView(LoginRequiredMixin, UpdateView):
    """Standaard view class voor Locatie bijwerken"""

    model = Locatie
    fields = "__all__"
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:locatiedetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update locatie"
        return context


class LocatieCreateView(LoginRequiredMixin, CreateView):
    """Standaard view class voor locatie aanmaken"""

    model = Locatie
    fields = "__all__"
    template_name = "WijnVoorraad/general_create_update.html"
    success_url = reverse_lazy("WijnVoorraad:locatielist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe locatie"
        return context


class LocatieListView(LoginRequiredMixin, ListView):
    """Standaard view class voor locatie overzicht"""

    model = Locatie
    context_object_name = "locaties"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Locaties"
        return context


class LocatieDetailView(LoginRequiredMixin, DetailView):
    """Standaard view class voor loactie details"""

    model = Locatie
    context_object_name = "locatie"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vakken"] = Vak.objects.filter(locatie=self.object)
        context["title"] = "Locatie"
        return context

    def post(self, request, *args, **kwargs):
        locatie_id = self.request.POST["object_id"]
        if locatie_id:
            locatie = Locatie.objects.get(pk=locatie_id)
            if "Verwijder" in self.request.POST:
                try:
                    locatie.delete()
                    messages.success(request, "Locatie is verwijderd")
                    url = reverse("WijnVoorraad:locatielist")
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse(
                        "WijnVoorraad:locatiedetail", kwargs=dict(pk=locatie_id)
                    )
            else:
                url = reverse("WijnVoorraad:locatiedetail", kwargs=dict(pk=locatie_id))
        else:
            url = reverse("WijnVoorraad:locatielist")
        return HttpResponseRedirect(url)


class WijnSoortUpdateView(LoginRequiredMixin, UpdateView):
    """Standaard view class voor wijnsoort bijwerken"""

    model = WijnSoort
    fields = "__all__"
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:wijnsoortdetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update wijnsoort"
        return context


class WijnSoortCreateView(LoginRequiredMixin, CreateView):
    """Standaard view class voor wijnsoort aanmaken"""

    model = WijnSoort
    fields = "__all__"
    template_name = "WijnVoorraad/general_create_update.html"
    success_url = reverse_lazy("WijnVoorraad:wijnsoortlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe wijnsoort"
        return context


class WijnSoortDetailView(LoginRequiredMixin, DetailView):
    """Standaard view class voor wijnsoort details"""

    model = WijnSoort
    context_object_name = "wijnsoort"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Wijnsoort"
        return context

    def post(self, request, *args, **kwargs):
        wijnsoort_id = self.request.POST["object_id"]
        if wijnsoort_id:
            wijnsoort = WijnSoort.objects.get(pk=wijnsoort_id)
            if "Verwijder" in self.request.POST:
                try:
                    wijnsoort.delete()
                    messages.success(request, "Wijnsoort is verwijderd")
                    url = reverse("WijnVoorraad:wijnsoortlist")
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse(
                        "WijnVoorraad:wijnsoortdetail", kwargs=dict(pk=wijnsoort_id)
                    )
            else:
                url = reverse(
                    "WijnVoorraad:wijnsoortdetail", kwargs=dict(pk=wijnsoort_id)
                )
        else:
            url = reverse("WijnVoorraad:wijnsoortlist")
        return HttpResponseRedirect(url)


class WijnSoortListView(LoginRequiredMixin, ListView):
    """Standaard view class voor wijnsoort overzicht"""

    model = WijnSoort
    context_object_name = "wijnsoorten"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Wijnsoorten"
        return context


class DruivenSoortUpdateView(LoginRequiredMixin, UpdateView):
    """Standaard view class voor bijwerken druiven soort"""

    model = DruivenSoort
    fields = "__all__"
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:druivensoortdetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update druivensoort"
        return context


class DruivenSoortCreateView(LoginRequiredMixin, CreateView):
    """Standaard view class voor aanmaken druiven soort"""

    model = DruivenSoort
    fields = "__all__"
    template_name = "WijnVoorraad/general_create_update.html"
    success_url = reverse_lazy("WijnVoorraad:druivensoortlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe druivensoort"
        return context


class DruivenSoortDetailView(LoginRequiredMixin, DetailView):
    """Standaard view class voor druiven soort details"""

    model = DruivenSoort
    context_object_name = "druivensoort"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Druivensoort"
        return context

    def post(self, request, *args, **kwargs):
        druivensoort_id = self.request.POST["object_id"]
        if druivensoort_id:
            druivensoort = DruivenSoort.objects.get(pk=druivensoort_id)
            if "Verwijder" in self.request.POST:
                try:
                    druivensoort.delete()
                    url = reverse("WijnVoorraad:druivensoortlist")
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse(
                        "WijnVoorraad:druivensoortdetail",
                        kwargs=dict(pk=druivensoort_id),
                    )
            else:
                url = reverse(
                    "WijnVoorraad:druivensoortdetail", kwargs=dict(pk=druivensoort_id)
                )
        else:
            url = reverse("WijnVoorraad:druivensoortlist")
        return HttpResponseRedirect(url)


class DruivenSoortListView(LoginRequiredMixin, ListView):
    """Standaard view class voor druiven soort overzicht"""

    model = DruivenSoort
    context_object_name = "druivensoorten"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Druivensoorten"
        return context


class DeelnemerUpdateView(LoginRequiredMixin, UpdateView):
    """Standaard view class voor bijwerken van Deelnemer"""

    form_class = DeelnemerForm
    model = Deelnemer
    template_name = "WijnVoorraad/general_create_update.html"

    def get_success_url(self) -> str:
        return reverse_lazy(
            "WijnVoorraad:deelnemerdetail",
            kwargs={"pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update deelnemer"
        return context


class DeelnemerCreateView(LoginRequiredMixin, CreateView):
    """Standaard view class voor aanmaken van Deelnemer"""

    form_class = DeelnemerForm
    model = Deelnemer
    template_name = "WijnVoorraad/general_create_update.html"
    success_url = reverse_lazy("WijnVoorraad:deelnemerlist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nieuwe deelnemer"
        return context


class DeelnemerDetailView(LoginRequiredMixin, DetailView):
    """Standaard view class voor de details van Deelnemer"""

    model = Deelnemer
    context_object_name = "deelnemer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Deelnemer"
        return context

    def post(self, request, *args, **kwargs):
        deelnemer_id = self.request.POST["object_id"]
        if deelnemer_id:
            deelnemer = Deelnemer.objects.get(pk=deelnemer_id)
            if "Verwijder" in self.request.POST:
                try:
                    deelnemer.delete()
                    messages.success(request, "Deelnemer is verwijderd")
                    url = reverse("WijnVoorraad:deelnemerlist")
                except:
                    messages.error(
                        request, "Verwijderen is niet mogelijk. Gerelateerde gegevens?"
                    )
                    url = reverse(
                        "WijnVoorraad:deelnemerdetail", kwargs=dict(pk=deelnemer_id)
                    )
            else:
                url = reverse(
                    "WijnVoorraad:deelnemerdetail", kwargs=dict(pk=deelnemer_id)
                )
        else:
            url = reverse("WijnVoorraad:deelnemerlist")
        return HttpResponseRedirect(url)


class DeelnemerListView(LoginRequiredMixin, ListView):
    """Standaard view class Deelnemer overzicht"""

    model = Deelnemer
    context_object_name = "deelnemers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Deelnemers"
        return context
