from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_view, name='home'),
    path('shop/', views.shop, name='shop'),
    path('service/', views.service, name='service'),
    path('fundament/', views.fundament, name='fundament'),
    path('installation/', views.installation, name='installation'),
    path('contacts/', views.contacts, name='contacts'),
    path('support/', views.feedback_view, name='support'),
    path('sistema-otopleniya/', views.sistemaotopleniya, name='sistemaotoplenia'),
]
