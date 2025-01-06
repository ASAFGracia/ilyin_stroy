from django.urls import path
from . import views

urlpatterns = [
    path('santehnika/', views.santehnika, name='santehnika-prices'),
]
