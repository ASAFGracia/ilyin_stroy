from django.conf import settings


def site_context(_request):
    return {
        "site_brand": settings.SITE_BRAND,
        "contact_phone": settings.CONTACT_PHONE,
        "contact_email": settings.CONTACT_EMAIL,
        "google_auth_enabled": settings.GOOGLE_AUTH_ENABLED,
    }
