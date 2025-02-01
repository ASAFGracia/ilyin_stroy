from django.contrib import admin
from .models import Article, ArticleImage, ArticleWriterRequest
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomUser

admin.site.register(ArticleImage)


class ArticleAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # Устанавливаем автора статьи как текущего пользователя
        if not obj.author:
            obj.author = request.user
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Оставляем только одобренных пользователей в поле author
        form.base_fields['author'].queryset = form.base_fields['author'].queryset.filter(is_approved=True)
        return form


admin.site.register(Article, ArticleAdmin)


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'unique_id', 'is_approved', 'is_verified')
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'is_approved',)
    search_fields = ('username', 'email', 'unique_id')
    ordering = ('id',)  # Сортировка по ID

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('unique_id',)}),
        ('Permissions', {'fields': ('is_approved', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Verification', {'fields': ('is_verified',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'unique_id', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('id',)

# Регистрируем кастомного пользователя в админке
admin.site.register(CustomUser, CustomUserAdmin)


class ArticleWriterRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username',)

admin.site.register(ArticleWriterRequest, ArticleWriterRequestAdmin)
