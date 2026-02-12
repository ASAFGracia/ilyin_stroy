from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_view, name='home'),
    path('orders/', views.order_request, name='orders'),
    path('articles/', views.articles, name='articles'),
    path('articles/templates/', views.article_templates, name='article_templates'),
    path('articles/new/', views.article_create, name='article_create'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('profile/', views.profile, name='profile'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('shop/', views.shop, name='shop'),
    path('service/', views.service, name='service'),
    path('fundament/', views.fundament, name='fundament'),
    path('installation/', views.installation, name='installation'),
    path('contacts/', views.contacts, name='contacts'),
    path('support/', views.feedback_view, name='support'),
    path('sistema-otopleniya/', views.sistemaotopleniya, name='sistemaotoplenia'),
]
