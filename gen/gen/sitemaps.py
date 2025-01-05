from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "daily"  # Частота изменений
    priority = 0.8        # Приоритет страницы

    def items(self):
        # Указываем имена маршрутов, которые нужно включить в sitemap
        return ['home', 'fundament', 'onas', 'contacts', 'support', 'sistemaotoplenia']

    def location(self, item):
        # Генерация URL на основе имени маршрута
        return reverse(item)

def items(self):
    print("Sitemap items generated:", ['home', 'fundament', 'onas', 'contacts', 'support', 'sistemaotoplenia'])
    return ['home', 'fundament', 'onas', 'contacts', 'support', 'sistemaotoplenia']
