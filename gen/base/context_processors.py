from django.conf import settings

from .access import is_admin_user


def site_context(request):
    owner_email = (settings.OWNER_EMAIL or "").lower()
    return {
        "site_brand": settings.SITE_BRAND,
        "contact_phone": settings.CONTACT_PHONE,
        "contact_email": settings.CONTACT_EMAIL,
        "owner_email": owner_email,
        "user_is_owner": bool(is_admin_user(request.user)),
        "telegram_bot_username": settings.TELEGRAM_BOT_USERNAME,
    }
