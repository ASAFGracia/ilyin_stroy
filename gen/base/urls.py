from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from .views import login_view, logout_view
from .views import profile_view
from django.conf import settings
from django.urls import path
from . import views


urlpatterns = [
    path('', views.contact_view, name='home'),
    path('fundament/', views.fundament, name='fundament'),
    path('about-us/', views.onas, name='onas'),
    path('contacts/', views.contacts, name='contacts'),
    path('support/', views.feedback_view, name='support'),
    path('sistema-otopleniya/', views.sistemaotopleniya, name='sistemaotoplenia'),
    path('articles/', views.article_list, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('new-article/', views.create_article, name='create_article'),
    path("register/", views.register, name="register"),
    path("verify_email/", views.verify_email, name="verify_email"),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('request-to-write-article/', views.request_to_write_article, name='request_to_write_article'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)