from django.urls import path

from . import views
from .views import VoorraadListView, DeelnemerListView, DeelnemerDetailView, WijnDetailView
from .views import OntvangstListView, OntvangstDetailView, VoorraadDetailView
from .views import OntvangstCreateView, WijnCreateView

app_name = 'WijnVoorraad'
urlpatterns = [
    path('', VoorraadListView.as_view(), name='voorraadlist'),
    path('voorraad/<int:wijn_id>/', VoorraadDetailView.as_view(), name='voorraaddetail'),
    path('wijn/<int:pk>/', WijnDetailView.as_view(), name='wijndetail'),
    path('wijn/create/', WijnCreateView.as_view(), name='wijn-create'),
    path('deelnemers/', DeelnemerListView.as_view(), name='deelnemerlist'),
    path('deelnemer/<int:pk>/', DeelnemerDetailView.as_view(), name='deelnemerdetail'),
    path('ontvangsten/', OntvangstListView.as_view(), name='ontvangstlist'),
    path('ontvangst/<int:pk>/', OntvangstDetailView.as_view(), name='ontvangstdetail'),
    path('change_context/', views.change_context, name='change_context'),
    path('ontvangst/create', OntvangstCreateView.as_view(), name='ontvangst-create'),
]
