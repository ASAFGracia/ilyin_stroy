from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify


phone_validator = RegexValidator(
    regex=r"^[0-9+\-\s()]{7,20}$",
    message="Введите корректный номер телефона.",
)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    nickname = models.CharField("Никнейм", max_length=60, blank=True)
    phone = models.CharField(
        "Телефон",
        max_length=20,
        blank=True,
        validators=[phone_validator],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self) -> str:
        return f"Профиль {self.user.username}"


class Article(models.Model):
    TEMPLATE_CHOICES = [
        ("custom", "Произвольная"),
        ("walls", "Стены"),
        ("lower_floor", "Полы нижнего этажа"),
        ("drainage", "Дренаж и коммуникации"),
    ]

    template_key = models.CharField(
        "Шаблон",
        max_length=30,
        choices=TEMPLATE_CHOICES,
        default="custom",
    )
    title = models.CharField("Заголовок", max_length=180)
    slug = models.SlugField("Slug", unique=True, max_length=200, blank=True)
    summary = models.TextField("Краткое описание", max_length=400, blank=True)
    content = models.TextField("Содержимое")
    is_published = models.BooleanField("Опубликовано", default=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:180]
            if not base_slug:
                base_slug = f"article-{uuid4().hex[:8]}"
            slug = base_slug
            n = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class OrderRequest(models.Model):
    CONTACT_CHOICES = [
        ("phone", "Позвонить"),
        ("email", "Написать по email"),
    ]
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В обработке"),
        ("done", "Закрыта"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=20, validators=[phone_validator])
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Комментарий", blank=True)
    contact_method = models.CharField(
        "Как связаться",
        max_length=20,
        choices=CONTACT_CHOICES,
        default="phone",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Заявка #{self.pk} - {self.name}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
