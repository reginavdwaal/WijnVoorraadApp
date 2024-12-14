"""All popup views and main function to handle the popup"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import escape

from WijnVoorraad.forms import (
    DeelnemerForm,
    DruivenSoortForm,
    LocatieForm,
    WijnForm,
    WijnSoortForm,
)


def handle_pop_add(request, add_form, field):

    zoeken = False
    wijnresponse = ""

    if request.method == "POST":
        zoeken = request.POST.get("ZOEK")

    if request.method == "POST" and not zoeken:

        form = add_form(request.POST, request.FILES)
        if form.is_valid():
            try:
                new_object = form.save()
            except form.ValidationError:
                new_object = None
            if new_object:
                response = (
                    '<script type="text/javascript">opener.dismissAddAnotherPopup(window,'
                    f'"{escape(new_object.pk)}", "{escape(new_object)}");</script>'
                )
                return HttpResponse(response)

    else:
        form = add_form()

        if zoeken:
            wijnresponse = "heel lekker wijn gevonden"

    page_context = {
        "form": form,
        "field": field,
        "wijngevonden": wijnresponse,
    }
    return render(request, "WijnVoorraad/general_popupadd.html", page_context)


@login_required
def standaard_locatie_create_popup_view(request):
    return handle_pop_add(request, LocatieForm, "StandaardLocatie")


@login_required
def locatie_create_popup_view(request):
    return handle_pop_add(request, LocatieForm, "locatie")


@login_required
def wijn_create_popup_view(request):
    return handle_pop_add(request, WijnForm, "wijn")


@login_required
def deelnemer_create_popup_view(request):
    return handle_pop_add(request, DeelnemerForm, "deelnemer")


@login_required
def deelnemers_create_popup_view(request):
    return handle_pop_add(request, DeelnemerForm, "deelnemers")


@login_required
def druiven_soort_create_popup_view(request):
    return handle_pop_add(request, DruivenSoortForm, "druivensoort")


@login_required
def wijn_druiven_soorten_create_popup_view(request):
    return handle_pop_add(request, DruivenSoortForm, "wijnDruivensoorten")


@login_required
def wijn_soort_create_popup_view(request):
    return handle_pop_add(request, WijnSoortForm, "wijnsoort")
