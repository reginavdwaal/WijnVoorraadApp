from django.urls import path

from . import views
from .views import VoorraadListView, DeelnemerListView, DeelnemerDetailView, WijnDetailView
from .views import OntvangstListView, OntvangstDetailView, VoorraadDetailView
from .views import OntvangstCreateView, OntvangstCreateView2, WijnCreateView, WijnListView, VoorraadVerplaaten

app_name = 'WijnVoorraad'
urlpatterns = [
    path('', VoorraadListView.as_view(), name='voorraadlist'),
    path('voorraad/<int:wijn_id>/', VoorraadDetailView.as_view(), name='voorraaddetail'),
    path('wijnen/', WijnListView.as_view(), name='wijnlist'),
    path('wijn/<int:pk>/', WijnDetailView.as_view(), name='wijndetail'),
    path('wijn/create/', WijnCreateView.as_view(), name='wijn-create'),
    path('deelnemers/', DeelnemerListView.as_view(), name='deelnemerlist'),
    path('deelnemer/<int:pk>/', DeelnemerDetailView.as_view(), name='deelnemerdetail'),
    path('ontvangsten/', OntvangstListView.as_view(), name='ontvangstlist'),
    path('ontvangst/<int:pk>/', OntvangstDetailView.as_view(), name='ontvangstdetail'),
    path('change_context/', views.change_context, name='change_context'),
    path('ontvangst/create', OntvangstCreateView.as_view(), name='ontvangst-create'),
    path('ontvangst/create2', OntvangstCreateView2.as_view(), name='ontvangst-create'),
    path('verplaatsen/<int:voorraad_id>/<int:aantal>', VoorraadVerplaaten.as_view(), name='verplaatsen'),
]
