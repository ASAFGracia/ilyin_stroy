from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('fundament/', views.fundament, name='fundament'),
    path('obout-us/', views.onas, name='onas'),
]