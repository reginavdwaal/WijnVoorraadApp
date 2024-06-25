"""Views voor de conversie van de oude database naar de nieuwe"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib import messages

# from WijnVoorraad.models_conversie import ConvDeelnemer
from WijnVoorraad.models_oudwijn import (
    OudDeelnemer,
    OudDruivensoort,
    OudLocatie,
    OudWijn,
    OudWijnDruivensoort,
    OudVoorraadmutatie,
)
from WijnVoorraad.models_conversie import (
    converteer_deelnemers,
    te_conv_deelnemers,
    converteer_druivensoorten,
    te_conv_druivensoorten,
    converteer_locaties,
    te_conv_locaties,
    converteer_wijnen,
    te_conv_wijnen,
    converteer_wijndruivensoorten,
    te_conv_wijndruivensoorten,
    converteer_voorraadmutaties,
    te_conv_voorraadmutaties,
)
from . import wijnvars


class StartConversieView(LoginRequiredMixin, TemplateView):
    template_name = "WijnVoorraad/startconversie.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["aantal_deelnemers_oud"] = OudDeelnemer.objects.count()
        conv = te_conv_deelnemers()
        context["aantal_deelnemers_te_conv"] = conv.count()
        context["message_list_deelnemer"] = wijnvars.get_session_extra_var(
            self.request, "message_list_deelnemer"
        )
        wijnvars.set_session_extra_var(self.request, "message_list_deelnemer", None)

        context["aantal_druivensoorten_oud"] = OudDruivensoort.objects.count()
        conv = te_conv_druivensoorten()
        context["aantal_druivensoorten_te_conv"] = conv.count()
        context["message_list_druivensoort"] = wijnvars.get_session_extra_var(
            self.request, "message_list_druivensoort"
        )
        wijnvars.set_session_extra_var(self.request, "message_list_druivensoort", None)

        context["aantal_locaties_oud"] = OudLocatie.objects.count()
        conv = te_conv_locaties()
        context["aantal_locaties_te_conv"] = conv.count()
        context["message_list_locatie"] = wijnvars.get_session_extra_var(
            self.request, "message_list_locatie"
        )
        wijnvars.set_session_extra_var(self.request, "message_list_locatie", None)

        context["aantal_wijnen_oud"] = OudWijn.objects.count()
        conv = te_conv_wijnen()
        context["aantal_wijnen_te_conv"] = conv.count()
        context["message_list_wijn"] = wijnvars.get_session_extra_var(
            self.request, "message_list_wijn"
        )
        wijnvars.set_session_extra_var(self.request, "message_list_wijn", None)

        context["aantal_wijndruivensoorten_oud"] = OudWijnDruivensoort.objects.count()
        conv = te_conv_wijndruivensoorten()
        context["aantal_wijndruivensoorten_te_conv"] = conv.count()
        context["message_list_wijndruivensoort"] = wijnvars.get_session_extra_var(
            self.request, "message_list_wijndruivensoort"
        )
        wijnvars.set_session_extra_var(
            self.request, "message_list_wijndruivensoort", None
        )

        context["aantal_voorraadmutaties_oud"] = OudVoorraadmutatie.objects.count()
        conv = te_conv_voorraadmutaties()
        context["aantal_voorraadmutaties_te_conv"] = conv.count()
        context["message_list_voorraadmutatie"] = wijnvars.get_session_extra_var(
            self.request, "message_list_voorraadmutatie"
        )
        wijnvars.set_session_extra_var(
            self.request, "message_list_voorraadmutatie", None
        )

        context["title"] = "Start conversie"
        return context

    def post(self, request, *args, **kwargs):
        if "InclAanmaken" in self.request.POST:
            InclAanmaken = True
        else:
            InclAanmaken = False
        if "DoCommit" in self.request.POST:
            DoCommit = True
        else:
            DoCommit = False
        if "StartConversieDeelnemer" in self.request.POST:
            convdata = converteer_deelnemers(InclAanmaken, DoCommit)
            wijnvars.set_session_extra_var(
                request, "message_list_deelnemer", convdata.message_list
            )
        elif "StartConversieDruivensoort" in self.request.POST:
            convdata = converteer_druivensoorten(InclAanmaken, DoCommit)
            wijnvars.set_session_extra_var(
                request, "message_list_druivensoort", convdata.message_list
            )
        elif "StartConversieLocatie" in self.request.POST:
            convdata = converteer_locaties(InclAanmaken, DoCommit)
            wijnvars.set_session_extra_var(
                request, "message_list_locatie", convdata.message_list
            )
        elif "StartConversieWijn" in self.request.POST:
            convdata = converteer_wijnen(InclAanmaken, DoCommit)
            wijnvars.set_session_extra_var(
                request, "message_list_wijn", convdata.message_list
            )
        elif "StartConversieWijnDruivensoort" in self.request.POST:
            convdata = converteer_wijndruivensoorten(InclAanmaken, DoCommit)
            wijnvars.set_session_extra_var(
                request, "message_list_wijndruivensoort", convdata.message_list
            )
        elif "StartConversieVoorraadmutatie" in self.request.POST:
            convdata = converteer_voorraadmutaties(InclAanmaken, DoCommit)
            wijnvars.set_session_extra_var(
                request, "message_list_voorraadmutatie", convdata.message_list
            )
        url = reverse("WijnVoorraad:startconversie")
        return HttpResponseRedirect(url)
