from django.urls import path

from . import views
from .views import DeelnemerListView, DeelnemerDetailView, VoorraadListView, WijnDetailView
from .views import OntvangstListView, OntvangstDetailView, OntvangstCreateView

app_name = 'WijnVoorraad'
urlpatterns = [
    path('', VoorraadListView.as_view(), name='voorraadlist'),
    path('<int:wijn_id>/', views.detail, name='detail'),
    path('<int:voorraad_id>/drink/', views.drink, name='drink'),
    path('wijn/<pk>/', WijnDetailView.as_view(), name='wijndetail'),
    path('deelnemers/', DeelnemerListView.as_view(), name='deelnemerlist'),
    path('deelnemer/<pk>/', DeelnemerDetailView.as_view(), name='deelnemerdetail'),
    path('ontvangsten/', OntvangstListView.as_view(), name='ontvangstlist'),
    path('ontvangst/<pk>/', OntvangstDetailView.as_view(), name='ontvangstdetail'),
    path('change_context/', views.change_context, name='change_context'),
    path('ontvangst/create', OntvangstCreateView.as_view(), name='ontvangst-create'),
]
