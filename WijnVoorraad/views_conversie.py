"""Views voor de conversie van de oude database naar de nieuwe"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib import messages

# from WijnVoorraad.models_conversie import ConvDeelnemer
from WijnVoorraad.models_oudwijn import OudDeelnemer, OudDruivensoort, OudLocatie
from WijnVoorraad.models_conversie import (
    converteer_deelnemers,
    te_conv_deelnemers,
    converteer_locaties,
    te_conv_locaties,
)
from WijnVoorraad.models_conversie import (
    converteer_druivensoorten,
    te_conv_druivensoorten,
)
from . import wijnvars


class StartConversieView(LoginRequiredMixin, TemplateView):
    template_name = "WijnVoorraad/startconversie.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["aantal_deelnemers_oud"] = OudDeelnemer.objects.count()
        conv_locaties = te_conv_deelnemers()
        context["aantal_deelnemers_te_conv"] = conv_locaties.count()
        context["message_deelnemer"] = wijnvars.get_session_extra_var(
            self.request, "message_deelnemer"
        )
        wijnvars.set_session_extra_var(self.request, "message_deelnemer", None)

        context["aantal_druivensoorten_oud"] = OudDruivensoort.objects.count()
        conv_locaties = te_conv_druivensoorten()
        context["aantal_druivensoorten_te_conv"] = conv_locaties.count()
        context["message_druivensoort"] = wijnvars.get_session_extra_var(
            self.request, "message_druivensoort"
        )
        wijnvars.set_session_extra_var(self.request, "message_druivensoort", None)

        context["aantal_locaties_oud"] = OudLocatie.objects.count()
        conv_locaties = te_conv_locaties()
        context["aantal_locaties_te_conv"] = conv_locaties.count()
        context["message_locatie"] = wijnvars.get_session_extra_var(
            self.request, "message_locatie"
        )
        wijnvars.set_session_extra_var(self.request, "message_locatie", None)

        context["title"] = "Start conversie"
        return context

    def post(self, request, *args, **kwargs):
        if "StartConversieDeelnemer" in self.request.POST:
            if "InclAanmaken" in self.request.POST:
                InclAanmaken = True
            else:
                InclAanmaken = False
            if "DoCommit" in self.request.POST:
                DoCommit = True
            else:
                DoCommit = False
            aantal_gekoppeld, aantal_aangemaakt = converteer_deelnemers(
                InclAanmaken, DoCommit
            )
            if DoCommit:
                message = "CONVERSIE: "
                message = message + "Aantal gekoppeld %s. " % (aantal_gekoppeld)
                if InclAanmaken:
                    message = message + "Aantal aangemaakt %s. " % (aantal_aangemaakt)
                else:
                    message = message + "Geen aangemaakt."
            else:
                message = "PROEFCONVERSIE: "
                message = message + "Aantal te koppelen %s. " % (aantal_gekoppeld)
                if InclAanmaken:
                    message = message + "Aantal aan te maken %s. " % (aantal_aangemaakt)

            wijnvars.set_session_extra_var(request, "message_deelnemer", message)
            url = reverse("WijnVoorraad:startconversie")
        elif "StartConversieDruivensoort" in self.request.POST:
            if "InclAanmaken" in self.request.POST:
                InclAanmaken = True
            else:
                InclAanmaken = False
            if "DoCommit" in self.request.POST:
                DoCommit = True
            else:
                DoCommit = False
            aantal_gekoppeld, aantal_aangemaakt = converteer_druivensoorten(
                InclAanmaken, DoCommit
            )
            if DoCommit:
                message = "CONVERSIE: "
                message = message + "Aantal gekoppeld %s. " % (aantal_gekoppeld)
                if InclAanmaken:
                    message = message + "Aantal aangemaakt %s. " % (aantal_aangemaakt)
                else:
                    message = message + "Geen aangemaakt."
            else:
                message = "PROEFCONVERSIE: "
                message = message + "Aantal te koppelen %s. " % (aantal_gekoppeld)
                if InclAanmaken:
                    message = message + "Aantal aan te maken %s. " % (aantal_aangemaakt)

            wijnvars.set_session_extra_var(request, "message_druivensoort", message)
            url = reverse("WijnVoorraad:startconversie")
        elif "StartConversieLocatie" in self.request.POST:
            if "InclAanmaken" in self.request.POST:
                InclAanmaken = True
            else:
                InclAanmaken = False
            if "DoCommit" in self.request.POST:
                DoCommit = True
            else:
                DoCommit = False
            aantal_gekoppeld, aantal_aangemaakt = converteer_locaties(
                InclAanmaken, DoCommit
            )
            if DoCommit:
                message = "CONVERSIE: "
                message = message + "Aantal gekoppeld %s. " % (aantal_gekoppeld)
                if InclAanmaken:
                    message = message + "Aantal aangemaakt %s. " % (aantal_aangemaakt)
                else:
                    message = message + "Geen aangemaakt."
            else:
                message = "PROEFCONVERSIE: "
                message = message + "Aantal te koppelen %s. " % (aantal_gekoppeld)
                if InclAanmaken:
                    message = message + "Aantal aan te maken %s. " % (aantal_aangemaakt)

            wijnvars.set_session_extra_var(request, "message_locatie", message)
            url = reverse("WijnVoorraad:startconversie")
        else:
            url = reverse("WijnVoorraad:voorraadlist")
        return HttpResponseRedirect(url)
