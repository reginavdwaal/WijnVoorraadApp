from django.urls import path

from . import views

app_name = 'WijnVoorraad'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:voorraad_id>/', views.detail, name='detail'),
    path('<int:voorraad_id>/drink/', views.drink, name='drink'),
]
