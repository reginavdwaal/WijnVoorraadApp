from django.urls import path, re_path, include

from . import views

app_name = "WijnVoorraad"
urlpatterns = [
    path(
        "gebruiker/<int:pk>/",
        views.GebruikerDetailView.as_view(),
        name="gebruikerdetail",
    ),
    path(
        "gebruiker/update/<int:pk>/",
        views.GebruikerUpdateView.as_view(),
        name="gebruiker-update",
    ),
    path("deelnemers/", views.DeelnemerListView.as_view(), name="deelnemerlist"),
    path(
        "deelnemer/<int:pk>/",
        views.DeelnemerDetailView.as_view(),
        name="deelnemerdetail",
    ),
    path(
        "deelnemer/create/",
        views.DeelnemerCreateView.as_view(),
        name="deelnemer-create",
    ),
    path(
        "deelnemer/update/<int:pk>/",
        views.DeelnemerUpdateView.as_view(),
        name="deelnemer-update",
    ),
    path(
        "deelnemer/popupadd/", views.DeelnemerCreatePopupView, name="deelnemer-popupadd"
    ),
    path(
        "deelnemers/popupadd/",
        views.DeelnemersCreatePopupView,
        name="deelnemers-popupadd",
    ),
    path(
        "druivensoorten/", views.DruivenSoortListView.as_view(), name="druivensoortlist"
    ),
    path(
        "druivensoort/<int:pk>/",
        views.DruivenSoortDetailView.as_view(),
        name="druivensoortdetail",
    ),
    path(
        "druivensoort/create/",
        views.DruivenSoortCreateView.as_view(),
        name="druivensoort-create",
    ),
    path(
        "druivensoort/update/<int:pk>/",
        views.DruivenSoortUpdateView.as_view(),
        name="druivensoort-update",
    ),
    path(
        "druivensoort/popupadd/",
        views.DruivenSoortCreatePopupView,
        name="druivensoort-popupadd",
    ),
    path(
        "wijnDruivensoorten/popupadd/",
        views.WijnDruivenSoortenCreatePopupView,
        name="wijndruivensoort-popupadd",
    ),
    path("wijnsoorten/", views.WijnSoortListView.as_view(), name="wijnsoortlist"),
    path(
        "wijnsoort/<int:pk>/",
        views.WijnSoortDetailView.as_view(),
        name="wijnsoortdetail",
    ),
    path(
        "wijnsoort/create/",
        views.WijnSoortCreateView.as_view(),
        name="wijnsoort-create",
    ),
    path(
        "wijnsoort/update/<int:pk>/",
        views.WijnSoortUpdateView.as_view(),
        name="wijnsoort-update",
    ),
    path(
        "wijnsoort/popupadd/", views.WijnSoortCreatePopupView, name="wijnsoort-popupadd"
    ),
    path("locaties/", views.LocatieListView.as_view(), name="locatielist"),
    path("locatie/<int:pk>/", views.LocatieDetailView.as_view(), name="locatiedetail"),
    path("locatie/create/", views.LocatieCreateView.as_view(), name="locatie-create"),
    path(
        "locatie/update/<int:pk>/",
        views.LocatieUpdateView.as_view(),
        name="locatie-update",
    ),
    path("locatie/popupadd/", views.LocatieCreatePopupView, name="locatie-popupadd"),
    path(
        "standaardLocatie/popupadd/",
        views.StandaardLocatieCreatePopupView,
        name="standaardlocatie-popupadd",
    ),
    path("vak/<int:pk>/", views.VakDetailView.as_view(), name="vakdetail"),
    path(
        "vak/create/<int:locatie_id>/", views.VakCreateView.as_view(), name="vak-create"
    ),
    path("vak/update/<int:pk>/", views.VakUpdateView.as_view(), name="vak-update"),
    path("wijnen/", views.WijnListView.as_view(), name="wijnlist"),
    path("wijnen/<str:fuzzy_selectie>/", views.WijnListView.as_view(), name="wijnlist"),
    path("wijn/<int:pk>/", views.WijnDetailView.as_view(), name="wijndetail"),
    path("wijn/create/", views.WijnCreateView.as_view(), name="wijn-create"),
    path("wijn/update/<int:pk>/", views.WijnUpdateView.as_view(), name="wijn-update"),
    path("wijn/popupadd/", views.WijnCreatePopupView, name="wijn-popupadd"),
    path("ontvangsten/", views.OntvangstListView.as_view(), name="ontvangstlist"),
    path(
        "ontvangst/<int:pk>/",
        views.OntvangstDetailView.as_view(),
        name="ontvangstdetail",
    ),
    path(
        "ontvangst/create", views.OntvangstCreateView.as_view(), name="ontvangst-create"
    ),
    path(
        "ontvangst/update/<int:pk>/",
        views.OntvangstUpdateView.as_view(),
        name="ontvangst-update",
    ),
    path("mutaties_uit/", views.MutatiesUitListView.as_view(), name="mutaties_uit"),
    path("mutaties_in/", views.MutatiesInListView.as_view(), name="mutaties_in"),
    path("mutatie/<int:pk>/", views.MutatieDetailView.as_view(), name="mutatiedetail"),
    path(
        "mutatie/update/<int:pk>/",
        views.MutatieUpdateView.as_view(),
        name="mutatie-update",
    ),
    path(
        "voorraad/<int:wijn_id>/<int:ontvangst_id>",
        views.VoorraadDetailView.as_view(),
        name="voorraaddetail",
    ),
    path(
        "voorraad/filter",
        views.VoorraadFilterView.as_view(),
        name="voorraadlist_filter",
    ),
    path(
        "voorraadontvangst/<int:ontvangst_id>/",
        views.VoorraadOntvangstView.as_view(),
        name="voorraadontvangst",
    ),
    path(
        "voorraadvakken/", views.VoorraadVakkenListView.as_view(), name="voorraadvakken"
    ),
    path(
        "verplaatsinvakken/<int:voorraad_id>/<int:nieuwe_locatie_id>/<int:aantal>",
        views.VoorraadVerplaatsInVakken.as_view(),
        name="verplaatsinvakken",
    ),
    path(
        "verplaatsen/<int:pk>", views.VoorraadVerplaatsen.as_view(), name="verplaatsen"
    ),
    path("change_context/", views.change_context, name="change_context"),
    path("", views.VoorraadListView.as_view(), name="voorraadlist"),
    path(
        "<int:wijnsoort_id_selectie>/",
        views.VoorraadListView.as_view(),
        name="voorraadlist",
    ),
    path(
        "q=<str:fuzzy_selectie>/",
        views.VoorraadListView.as_view(),
        name="voorraadlist",
    ),
    path(
        "<int:wijnsoort_id_selectie>/<str:fuzzy_selectie>/",
        views.VoorraadListView.as_view(),
        name="voorraadlist",
    ),
]
