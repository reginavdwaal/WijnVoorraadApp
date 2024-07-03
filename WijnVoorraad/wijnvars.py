from django.http import HttpResponseRedirect
from django.urls import reverse
import re
from .models import Deelnemer, Locatie, WijnSoort


def unified_wijnsoort(wijnsoort_omschrijving):
    # Mogelijke outputwaarden: rood, wit, rose, mousserend,rodeport, witteport, onbekend
    wijnsoort_omschrijving = wijnsoort_omschrijving.lower()
    wijnsoort_omschrijving = re.sub("[^a-z]", "", wijnsoort_omschrijving)
    if wijnsoort_omschrijving == "portrood":
        wijnsoort_omschrijving = "rodeport"
    if wijnsoort_omschrijving == "portwit":
        wijnsoort_omschrijving = "witteport"
    if wijnsoort_omschrijving not in [
        "rood",
        "wit",
        "rose",
        "mousserend",
        "rodeport",
        "witteport",
    ]:
        wijnsoort_omschrijving = "onbekend"
    return wijnsoort_omschrijving


def set_session_deelnemer(request, deelnemer_id):
    d = Deelnemer.objects.get(pk=deelnemer_id)
    request.session["deelnemer_id"] = deelnemer_id
    request.session["deelnemer_naam"] = d.naam
    return request


def get_session_deelnemer_id(request):
    set_initial_user_session(request)
    deelnemer_id = request.session.get("deelnemer_id", None)
    return deelnemer_id


def get_session_deelnemer_naam(request):
    set_initial_user_session(request)
    deelnemer_naam = request.session.get("deelnemer_naam", None)
    return deelnemer_naam


def get_session_deelnemer(request):
    d_id = get_session_deelnemer_id(request)
    deelnemer = Deelnemer.objects.get(pk=d_id)
    return deelnemer


def set_session_deelnemer_list(request, deelnemer_list):
    request.session["deelnemer_list"] = deelnemer_list
    return request


def get_session_deelnemer_list(request):
    set_initial_user_session(request)
    deelnemer_list = request.session.get("deelnemer_list", None)
    return deelnemer_list


def set_session_locatie(request, locatie_id):
    l = Locatie.objects.get(pk=locatie_id)
    request.session["locatie_id"] = locatie_id
    request.session["locatie_omschrijving"] = l.omschrijving
    return request


def get_session_locatie_id(request):
    set_initial_user_session(request)
    locatie_id = request.session.get("locatie_id", None)
    return locatie_id


def get_session_locatie_omschrijving(request):
    set_initial_user_session(request)
    locatie_omschrijving = request.session.get("locatie_omschrijving", None)
    return locatie_omschrijving


def get_session_locatie(request):
    l_id = get_session_locatie_id(request)
    locatie = Locatie.objects.get(pk=l_id)
    return locatie


def set_session_locatie_list(request, locatie_list):
    request.session["locatie_list"] = locatie_list
    return request


def get_session_locatie_list(request):
    set_initial_user_session(request)
    locatie_list = request.session.get("locatie_list", None)
    return locatie_list


def set_session_wijnsoort_id(request, wijnsoort_id):
    if wijnsoort_id:
        ws = WijnSoort.objects.get(pk=wijnsoort_id)
    else:
        ws = None
    set_session_wijnsoort(request, ws)
    return request


def set_session_wijnsoort(request, wijnsoort):
    if wijnsoort:
        request.session["wijnsoort_id"] = wijnsoort.id
        request.session["wijnsoort_omschrijving"] = unified_wijnsoort(
            wijnsoort.omschrijving
        )
    else:
        request.session["wijnsoort_id"] = None
        request.session["wijnsoort_omschrijving"] = None
    return request


def set_session_wijnsoort_rood(request):
    ws = WijnSoort.objects.get(omschrijving__iexact="Rood")
    set_session_wijnsoort(request, ws)
    return request


def set_session_wijnsoort_wit(request):
    ws = WijnSoort.objects.get(omschrijving__iexact="Wit")
    set_session_wijnsoort(request, ws)
    return request


def set_session_wijnsoort_rose(request):
    ws = WijnSoort.objects.get(omschrijving__iexact="Rose")
    set_session_wijnsoort(request, ws)
    return request


def get_session_wijnsoort_id(request):
    wijnsoort_id = request.session.get("wijnsoort_id", None)
    return wijnsoort_id


def get_session_wijnsoort_omschrijving(request):
    wijnsoort_omschrijving = request.session.get("wijnsoort_omschrijving", None)
    return wijnsoort_omschrijving


def set_session_fuzzy_selectie(request, fuzzy_selectie):
    if fuzzy_selectie:
        try:
            int(fuzzy_selectie)
            request.session["fuzzy_selectie"] = fuzzy_selectie + "num"
        except ValueError:
            request.session["fuzzy_selectie"] = fuzzy_selectie
    else:
        request.session["fuzzy_selectie"] = fuzzy_selectie
    return request


def get_session_fuzzy_selectie(request):
    fuzzy_selectie = request.session.get("fuzzy_selectie", None)
    if fuzzy_selectie:
        if "num" in fuzzy_selectie:
            try:
                num = int(fuzzy_selectie[0:-3])
                fuzzy_selectie = str(num)
            except ValueError:
                pass
    return fuzzy_selectie


def set_session_return_url(request, return_url):
    request.session["return_url"] = return_url
    return request


def get_session_return_url(request):
    return_url = request.session.get("return_url")
    return return_url


# def set_session_ontvangst_id (request, ontvangst_id):
#     request.session["ontvangst_id"] = ontvangst_id
#     return request

# def get_session_ontvangst_id (request):
#     ontvangst_id = request.session.get("ontvangst_id", None)
#     return ontvangst_id


def set_initial_user_session(request):
    if request.session.get("initial_set", None) is None:
        du = request.user.deelnemers.all()
        if du.count() >= 1:
            set_session_deelnemer(request, du[0].id)
            set_session_locatie(request, du[0].standaardLocatie.id)
    request.session["initial_set"] = True


def reset_session_vars(request):
    request.session["initial_set"] = None
    set_initial_user_session(request)
    set_session_wijnsoort_id(request, None)
    set_session_fuzzy_selectie(request, None)


def set_context_deelnemer_list(context):
    d = Deelnemer.objects.all()
    context["deelnemer_list"] = d
    return context


def set_context_locatie_list(context):
    l = Locatie.objects.all()
    context["locatie_list"] = l
    return context


def set_context_return_url(context, return_url):
    context["return_url"] = return_url
    return context


def set_context_default(context, return_url):
    set_context_deelnemer_list(context)
    set_context_locatie_list(context)
    set_context_return_url(context, return_url)
    return context


def set_context_filter_options(context, request, return_url):
    fuzzy_selectie = get_session_fuzzy_selectie(request)
    if fuzzy_selectie:
        context["fuzzy_selectie"] = fuzzy_selectie
    set_session_return_url(request, return_url)
    return context


def set_session_extra_var(request, extra_var_name, extra_var_value):
    request.session[extra_var_name] = extra_var_value
    return request


def get_session_extra_var(request, extra_var_name):
    extra_var_value = request.session.get(extra_var_name, None)
    return extra_var_value


def handle_filter_options_post(request):
    if "FilterClear" in request.POST:
        reset_session_vars(request)
    else:
        fuzzy_selectie = request.POST["fuzzy_selectie"]
        set_session_fuzzy_selectie(request, fuzzy_selectie)
        ws_rood = request.POST.get("ws_rood")
        if ws_rood:
            if get_session_wijnsoort_omschrijving(request) == "rood":
                set_session_wijnsoort(request, None)
            else:
                set_session_wijnsoort_rood(request)
        ws_wit = request.POST.get("ws_wit")
        if ws_wit:
            if get_session_wijnsoort_omschrijving(request) == "wit":
                set_session_wijnsoort(request, None)
            else:
                set_session_wijnsoort_wit(request)
        ws_rose = request.POST.get("ws_rose")
        if ws_rose:
            if get_session_wijnsoort_omschrijving(request) == "rose":
                set_session_wijnsoort(request, None)
            else:
                set_session_wijnsoort_rose(request)
