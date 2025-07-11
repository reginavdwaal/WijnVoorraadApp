from django.urls import path

import WijnVoorraad.views_basis
import WijnVoorraad.views_popup

from . import views

app_name = "WijnVoorraad"
urlpatterns = [
    path(
        "deelnemers/",
        WijnVoorraad.views_basis.DeelnemerListView.as_view(),
        name="deelnemerlist",
    ),
    path(
        "deelnemer/<int:pk>/",
        WijnVoorraad.views_basis.DeelnemerDetailView.as_view(),
        name="deelnemerdetail",
    ),
    path(
        "deelnemer/create/",
        WijnVoorraad.views_basis.DeelnemerCreateView.as_view(),
        name="deelnemer-create",
    ),
    path(
        "deelnemer/update/<int:pk>/",
        WijnVoorraad.views_basis.DeelnemerUpdateView.as_view(),
        name="deelnemer-update",
    ),
    path(
        "deelnemer/popupadd/",
        WijnVoorraad.views_popup.deelnemer_create_popup_view,
        name="deelnemer-popupadd",
    ),
    path(
        "deelnemers/popupadd/",
        WijnVoorraad.views_popup.deelnemers_create_popup_view,
        name="deelnemers-popupadd",
    ),
    path(
        "druivensoorten/",
        WijnVoorraad.views_basis.DruivenSoortListView.as_view(),
        name="druivensoortlist",
    ),
    path(
        "druivensoort/<int:pk>/",
        WijnVoorraad.views_basis.DruivenSoortDetailView.as_view(),
        name="druivensoortdetail",
    ),
    path(
        "druivensoort/create/",
        WijnVoorraad.views_basis.DruivenSoortCreateView.as_view(),
        name="druivensoort-create",
    ),
    path(
        "druivensoort/update/<int:pk>/",
        WijnVoorraad.views_basis.DruivenSoortUpdateView.as_view(),
        name="druivensoort-update",
    ),
    path(
        "druivensoort/popupadd/",
        WijnVoorraad.views_popup.druiven_soort_create_popup_view,
        name="druivensoort-popupadd",
    ),
    path(
        "gebruiker/<int:pk>/",
        WijnVoorraad.views_basis.GebruikerDetailView.as_view(),
        name="gebruikerdetail",
    ),
    path(
        "gebruiker/update/<int:pk>/",
        WijnVoorraad.views_basis.GebruikerUpdateView.as_view(),
        name="gebruiker-update",
    ),
    path(
        "locaties/",
        WijnVoorraad.views_basis.LocatieListView.as_view(),
        name="locatielist",
    ),
    path(
        "locatie/<int:pk>/",
        WijnVoorraad.views_basis.LocatieDetailView.as_view(),
        name="locatiedetail",
    ),
    path(
        "locatie/create/",
        WijnVoorraad.views_basis.LocatieCreateView.as_view(),
        name="locatie-create",
    ),
    path(
        "locatie/update/<int:pk>/",
        WijnVoorraad.views_basis.LocatieUpdateView.as_view(),
        name="locatie-update",
    ),
    path(
        "locatie/popupadd/",
        WijnVoorraad.views_popup.locatie_create_popup_view,
        name="locatie-popupadd",
    ),
    path("mutaties/", views.MutatieListView.as_view(), name="mutatielist"),
    path("mutaties_uit/", views.MutatieUitListView.as_view(), name="mutatielist_uit"),
    path("mutaties_in/", views.MutatieInListView.as_view(), name="mutatielist_in"),
    path("mutatie/<int:pk>/", views.MutatieDetailView.as_view(), name="mutatiedetail"),
    path(
        "mutatie/create/",
        views.MutatieCreateView.as_view(),
        name="mutatie-create",
    ),
    path(
        "mutatie/create/<int:ontvangst_id>/",
        views.MutatieCreateView.as_view(),
        name="mutatie-create",
    ),
    path(
        "mutatie/create/<int:ontvangst_id>/<int:voorraad_id>",
        views.MutatieCreateView.as_view(),
        name="mutatie-create",
    ),
    path(
        "mutatie/update/<int:pk>/",
        views.MutatieUpdateView.as_view(),
        name="mutatie-update",
    ),
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
        "ontvangst/create/<int:wijn_id>/",
        views.OntvangstCreateView.as_view(),
        name="ontvangst-create",
    ),
    path(
        "ontvangst/update/<int:pk>/",
        views.OntvangstUpdateView.as_view(),
        name="ontvangst-update",
    ),
    path(
        "standaardLocatie/popupadd/",
        WijnVoorraad.views_popup.standaard_locatie_create_popup_view,
        name="standaardlocatie-popupadd",
    ),
    path(
        "vak/<int:pk>/",
        WijnVoorraad.views_basis.VakDetailView.as_view(),
        name="vakdetail",
    ),
    path(
        "vak/create/<int:locatie_id>/",
        WijnVoorraad.views_basis.VakCreateView.as_view(),
        name="vak-create",
    ),
    path(
        "vak/update/<int:pk>/",
        WijnVoorraad.views_basis.VakUpdateView.as_view(),
        name="vak-update",
    ),
    path(
        "verplaatsinvakken/<int:voorraad_id>/<int:nieuwe_locatie_id>/<int:aantal>",
        views.VoorraadVerplaatsInVakken.as_view(),
        name="verplaatsinvakken",
    ),
    path(
        "verplaatsen/<int:pk>", views.VoorraadVerplaatsen.as_view(), name="verplaatsen"
    ),
    path(
        "voorraad/<int:locatie_id>/<int:wijn_id>/<int:ontvangst_id>",
        views.VoorraadDetailView.as_view(),
        name="voorraaddetail",
    ),
    path(
        "voorraad/filter",
        views.VoorraadFilterView.as_view(),
        name="voorraadlist_filter",
    ),
    path(
        "ontvangstvoorraad/<int:ontvangst_id>/",
        views.OntvangstVoorraadView.as_view(),
        name="ontvangstvoorraad",
    ),
    path(
        "voorraadvakken/",
        views.VoorraadVakkenListView.as_view(),
        name="voorraadvakkenlist",
    ),
    path("wijnen/", views.WijnListView.as_view(), name="wijnlist"),
    path("wijn/<int:pk>/", views.WijnDetailView.as_view(), name="wijndetail"),
    path("wijn/create/", views.WijnCreateView.as_view(), name="wijn-create"),
    path("wijn/update/<int:pk>/", views.WijnUpdateView.as_view(), name="wijn-update"),
    path(
        "wijn/opzoeken/<int:pk>/", views.WijnSearchView.as_view(), name="wijn-opzoeken"
    ),
    path(
        "wijn/popupadd/",
        WijnVoorraad.views_popup.wijn_create_popup_view,
        name="wijn-popupadd",
    ),
    path(
        "wijnDruivensoorten/popupadd/",
        WijnVoorraad.views_popup.wijn_druiven_soorten_create_popup_view,
        name="wijndruivensoort-popupadd",
    ),
    path(
        "wijnsoorten/",
        WijnVoorraad.views_basis.WijnSoortListView.as_view(),
        name="wijnsoortlist",
    ),
    path(
        "wijnsoort/<int:pk>/",
        WijnVoorraad.views_basis.WijnSoortDetailView.as_view(),
        name="wijnsoortdetail",
    ),
    path(
        "wijnsoort/create/",
        WijnVoorraad.views_basis.WijnSoortCreateView.as_view(),
        name="wijnsoort-create",
    ),
    path(
        "wijnsoort/update/<int:pk>/",
        WijnVoorraad.views_basis.WijnSoortUpdateView.as_view(),
        name="wijnsoort-update",
    ),
    path(
        "wijnsoort/popupadd/",
        WijnVoorraad.views_popup.wijn_soort_create_popup_view,
        name="wijnsoort-popupadd",
    ),
    path("", views.VoorraadListView.as_view(), name="voorraadlist"),
    path("AI-zoeken/", views.AIview.as_view(), name="AI-zoeken"),
    path("bestellingen/", views.BestellingListView.as_view(), name="bestellinglist"),
    path(
        "bestelling/<int:pk>/",
        views.BestellingDetailView.as_view(),
        name="bestellingdetail",
    ),
    path(
        "bestelling/create",
        views.BestellingCreateView.as_view(),
        name="bestelling-create",
    ),
    path(
        "bestelling/update/<int:pk>/",
        views.BestellingUpdateView.as_view(),
        name="bestelling-update",
    ),
    path(
        "bestellingregelsselecteren/<int:bestelling_id>",
        views.BestellingRegelsSelecteren.as_view(),
        name="bestellingregelsselecteren",
    ),
    path(
        "bestellingregel/update/<int:pk>/",
        views.BestellingRegelUpdateView.as_view(),
        name="bestellingregel-update",
    ),
    path(
        "bestellingenverzamelen/",
        views.BestellingenVerzamelen.as_view(),
        name="bestellingenverzamelen",
    ),
    path(
        "bestellingverzamelendetail/<int:pk>/",
        views.BestellingVerzamelenDetail.as_view(),
        name="bestellingverzamelendetail",
    ),
    path(
        "bestellingregelverplaatsen/<int:pk>",
        views.BestellingRegelVerplaatsen.as_view(),
        name="bestellingregelverplaatsen",
    ),
    path(
        "bestellingregelverplaatsinvakken/<int:bestellingregel_id>/<int:nieuwe_locatie_id>/<int:aantal>",
        views.BestellingregelVerplaatsInVakken.as_view(),
        name="bestellingregelverplaatsinvakken",
    ),
    path(
        "voorraadcontroleren/",
        views.VoorraadControleren.as_view(),
        name="voorraadcontroleren",
    ),
]
