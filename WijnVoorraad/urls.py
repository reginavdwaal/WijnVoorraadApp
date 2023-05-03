from django.urls import path

from . import views
from .views import DeelnemerListView, DeelnemerDetailView

app_name = 'WijnVoorraad'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:voorraad_id>/', views.detail, name='detail'),
    path('<int:voorraad_id>/drink/', views.drink, name='drink'),
    path('deelnemers/', DeelnemerListView.as_view(), name='deelnemer_list'),
    path('deelnemer/<pk>/', DeelnemerDetailView.as_view(), name='deelnemer_detail')
]
