from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from gen.sitemaps import StaticViewSitemap

# Определение карты сайта
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', include('base.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('prices/', include('prices.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),  # Путь к sitemap.xml
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
