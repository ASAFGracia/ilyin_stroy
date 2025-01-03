from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from base import views

urlpatterns = [
    path('', include('base.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)