from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_view, name='home'),
    path('fundament/', views.fundament, name='fundament'),
    path('obout-us/', views.onas, name='onas'),
    path('contacts/', views.contacts, name='contacts'),
    path('support/', views.feedback_view, name='support'),
    path('sistema-otopleniya/', views.sistemaotopleniya, name='sistemaotoplenia'),
]
