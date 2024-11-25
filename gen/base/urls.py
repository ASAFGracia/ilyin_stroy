from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('fundament/', views.fundament, name='fundament'),
    path('obout-us/', views.onas, name='onas'),
    path('contacts/', views.contacts, name='contacts'),
    path('support/', views.support, name='support'),
    path('sistema-otopleniya/', views.sistemaotopleniya, name='sistemaotoplenia'),
]