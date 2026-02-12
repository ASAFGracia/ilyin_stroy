from django.urls import path

from . import views

urlpatterns = [
    path("", views.contact_view, name="home"),
    path("auth/login/", views.auth_login_request, name="auth_login_request"),
    path("auth/verify/", views.auth_verify_code, name="auth_verify_code"),
    path("auth/telegram/", views.auth_telegram_request, name="auth_telegram_request"),
    path("auth/telegram/verify/", views.auth_telegram_verify, name="auth_telegram_verify"),
    path("auth/logout/", views.auth_logout, name="auth_logout"),
    path("orders/", views.order_request, name="orders"),
    path("articles/", views.articles, name="articles"),
    path("articles/submit/", views.article_submit_request, name="article_submit_request"),
    path("articles/templates/", views.article_templates, name="article_templates"),
    path("articles/new/", views.article_create, name="article_create"),
    path("articles/<slug:slug>/", views.article_detail, name="article_detail"),
    path("owner/", views.owner_dashboard, name="owner_dashboard"),
    path(
        "owner/submissions/<int:submission_id>/approve/",
        views.owner_submission_approve,
        name="owner_submission_approve",
    ),
    path(
        "owner/submissions/<int:submission_id>/reject/",
        views.owner_submission_reject,
        name="owner_submission_reject",
    ),
    path("owner/admins/grant/", views.owner_admin_grant, name="owner_admin_grant"),
    path(
        "owner/admins/<int:access_id>/revoke/",
        views.owner_admin_revoke,
        name="owner_admin_revoke",
    ),
    path(
        "owner/admins/<int:access_id>/activate/",
        views.owner_admin_activate,
        name="owner_admin_activate",
    ),
    path(
        "owner/orders/<int:order_id>/status/",
        views.owner_order_status_update,
        name="owner_order_status_update",
    ),
    path(
        "owner/preorders/<int:preorder_id>/status/",
        views.owner_preorder_status_update,
        name="owner_preorder_status_update",
    ),
    path("profile/", views.profile, name="profile"),
    path("profile/settings/", views.profile_settings, name="profile_settings"),
    path("shop/", views.shop, name="shop"),
    path("service/", views.service, name="service"),
    path("fundament/", views.fundament, name="fundament"),
    path("installation/", views.installation, name="installation"),
    path("contacts/", views.contacts, name="contacts"),
    path("support/", views.feedback_view, name="support"),
    path("sistema-otopleniya/", views.sistemaotopleniya, name="sistemaotoplenia"),
]
