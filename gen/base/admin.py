from django.contrib import admin

from .models import Article, OrderRequest, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nickname", "phone", "updated_at")
    search_fields = ("user__username", "user__email", "nickname", "phone")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "template_key", "is_published", "created_at")
    list_filter = ("template_key", "is_published", "created_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "contact_method", "status", "created_at")
    list_filter = ("status", "contact_method", "created_at")
    search_fields = ("name", "phone", "email", "message")
