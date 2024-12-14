from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('', views.index, name='home'),
    path('fundament/', views.fundament, name='fundament'),
    path('about-us/', views.onas, name='onas'),
    path('contacts/', views.contacts, name='contacts'),
    path('support/', views.support, name='support'),
    path('success/', views.success_page, name='success_page'),
    path('sistema-otopleniya/', views.sistemaotopleniya, name='sistemaotoplenia'),
    path('select-form/', choose_form, name='choose_form'),
    path('products/add/', add_product, name='add_product'),
    path('products/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('products/', product_list, name='product_list'),
    path('delete_product/<int:pk>/', delete_product, name='delete_product'),
    path('categorys/add/', add_category, name='add_category'),
    path('categorys/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('categorys/', category_list, name='category_list'),
    path('delete_category/<int:pk>/', delete_category, name='delete_category'),
    path('categorys/current-month/', current_month_categories, name='current_month_categories'),
    path('products/category/<int:category_id>/', products_by_category, name='products_by_category'),
]