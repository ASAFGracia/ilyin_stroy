from django.contrib import admin

from .models import (
    AdminEmailAccess,
    Article,
    ArticleImage,
    ArticleSubmission,
    EmailAuthCode,
    OrderRequest,
    Product,
    ProductCategory,
    Profile,
    ShopPreorder,
    SubmissionImage,
    TelegramAuthCode,
)


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 0


class SubmissionImageInline(admin.TabularInline):
    model = SubmissionImage
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nickname", "phone", "updated_at")
    search_fields = ("user__username", "user__email", "nickname", "phone")


@admin.register(EmailAuthCode)
class EmailAuthCodeAdmin(admin.ModelAdmin):
    list_display = ("email", "expires_at", "attempts_left", "is_used", "created_at")
    list_filter = ("is_used", "created_at")
    search_fields = ("email",)


@admin.register(TelegramAuthCode)
class TelegramAuthCodeAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "chat_id",
        "expires_at",
        "attempts_left",
        "is_used",
        "created_at",
    )
    list_filter = ("is_used", "created_at")
    search_fields = ("email", "chat_id")


@admin.register(AdminEmailAccess)
class AdminEmailAccessAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "granted_by", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email", "note", "granted_by__email")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "template_key", "is_published", "created_at")
    list_filter = ("template_key", "is_published", "created_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ArticleImageInline]


@admin.register(ArticleSubmission)
class ArticleSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "summary", "content", "user__email")
    inlines = [SubmissionImageInline]


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "contact_method", "status", "created_at")
    list_filter = ("status", "contact_method", "created_at")
    search_fields = ("name", "phone", "email", "message", "article__title")


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ShopPreorder)
class ShopPreorderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "desired_item", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("desired_item", "phone", "email", "user__email")
