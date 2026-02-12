from __future__ import annotations

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def is_admin_email(email: str | None) -> bool:
    normalized = normalize_email(email)
    if not normalized:
        return False

    owner_email = normalize_email(getattr(settings, "OWNER_EMAIL", ""))
    if owner_email and normalized == owner_email:
        return True

    try:
        from .models import AdminEmailAccess

        return AdminEmailAccess.objects.filter(email=normalized, is_active=True).exists()
    except (OperationalError, ProgrammingError):
        # Migrations may not be applied yet.
        return False


def is_admin_user(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return is_admin_email(getattr(user, "email", ""))
