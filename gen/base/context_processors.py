from django.conf import settings


def site_context(request):
    owner_email = (settings.OWNER_EMAIL or "").lower()
    current_email = (getattr(request.user, "email", "") or "").lower()
    return {
        "site_brand": settings.SITE_BRAND,
        "contact_phone": settings.CONTACT_PHONE,
        "contact_email": settings.CONTACT_EMAIL,
        "owner_email": owner_email,
        "user_is_owner": bool(request.user.is_authenticated and current_email == owner_email),
    }
