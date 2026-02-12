from datetime import timedelta
from uuid import uuid4
import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify


phone_validator = RegexValidator(
    regex=r"^[0-9+\-\s()]{7,20}$",
    message="Введите корректный номер телефона.",
)


def validate_image_size(file_obj):
    max_bytes = 10 * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValidationError("Размер изображения не должен превышать 10 MB.")


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


class EmailAuthCode(models.Model):
    email = models.EmailField("Email", db_index=True)
    code_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    attempts_left = models.PositiveSmallIntegerField(default=5)
    is_used = models.BooleanField(default=False)
    requested_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Код авторизации"
        verbose_name_plural = "Коды авторизации"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Код для {self.email}"

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def verify_code(self, raw_code: str) -> bool:
        if self.is_used or self.is_expired() or self.attempts_left <= 0:
            return False
        if check_password(raw_code, self.code_hash):
            self.is_used = True
            self.save(update_fields=["is_used"])
            return True
        self.attempts_left = max(0, self.attempts_left - 1)
        if self.attempts_left == 0:
            self.is_used = True
            self.save(update_fields=["attempts_left", "is_used"])
        else:
            self.save(update_fields=["attempts_left"])
        return False

    @classmethod
    def issue_code(
        cls,
        *,
        email: str,
        requested_ip: str | None = None,
        ttl_minutes: int = 10,
        max_attempts: int = 5,
    ) -> tuple["EmailAuthCode", str]:
        normalized_email = email.strip().lower()
        cls.objects.filter(email=normalized_email, is_used=False).update(is_used=True)
        raw_code = f"{secrets.randbelow(1_000_000):06d}"
        obj = cls.objects.create(
            email=normalized_email,
            code_hash=make_password(raw_code),
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
            attempts_left=max_attempts,
            requested_ip=requested_ip,
        )
        return obj, raw_code


class TelegramAuthCode(models.Model):
    email = models.EmailField("Email", db_index=True)
    chat_id = models.BigIntegerField("Telegram chat id", db_index=True)
    code_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    attempts_left = models.PositiveSmallIntegerField(default=5)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Telegram код авторизации"
        verbose_name_plural = "Telegram коды авторизации"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Telegram код для {self.email} ({self.chat_id})"

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def verify_code(self, raw_code: str) -> bool:
        if self.is_used or self.is_expired() or self.attempts_left <= 0:
            return False
        if check_password(raw_code, self.code_hash):
            self.is_used = True
            self.save(update_fields=["is_used"])
            return True
        self.attempts_left = max(0, self.attempts_left - 1)
        if self.attempts_left == 0:
            self.is_used = True
            self.save(update_fields=["attempts_left", "is_used"])
        else:
            self.save(update_fields=["attempts_left"])
        return False

    @classmethod
    def issue_code(
        cls,
        *,
        email: str,
        chat_id: int,
        ttl_minutes: int = 10,
        max_attempts: int = 5,
    ) -> tuple["TelegramAuthCode", str]:
        normalized_email = email.strip().lower()
        cls.objects.filter(
            email=normalized_email,
            chat_id=chat_id,
            is_used=False,
        ).update(is_used=True)
        raw_code = f"{secrets.randbelow(1_000_000):06d}"
        obj = cls.objects.create(
            email=normalized_email,
            chat_id=chat_id,
            code_hash=make_password(raw_code),
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
            attempts_left=max_attempts,
        )
        return obj, raw_code


class AdminEmailAccess(models.Model):
    email = models.EmailField("Email", unique=True, db_index=True)
    is_active = models.BooleanField("Активен", default=True)
    note = models.CharField("Заметка", max_length=255, blank=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_admin_accesses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Доступ администратора по email"
        verbose_name_plural = "Доступы администраторов по email"
        ordering = ("email",)

    def __str__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"{self.email} ({status})"

    def save(self, *args, **kwargs):
        self.email = (self.email or "").strip().lower()
        super().save(*args, **kwargs)


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
    content = models.TextField("Содержимое", max_length=20000)
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


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        "Изображение",
        upload_to="articles/%Y/%m/",
        validators=[validate_image_size],
    )
    caption = models.CharField("Подпись", max_length=140, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Изображение статьи"
        verbose_name_plural = "Изображения статей"
        ordering = ("sort_order", "id")

    def __str__(self) -> str:
        return f"Изображение статьи #{self.article_id}"


class ArticleSubmission(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "На модерации"),
        (STATUS_APPROVED, "Одобрена"),
        (STATUS_REJECTED, "Отклонена"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="article_submissions",
    )
    title = models.CharField("Заголовок", max_length=180)
    summary = models.TextField("Краткое описание", max_length=400, blank=True)
    content = models.TextField("Текст", max_length=20000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_article_submissions",
    )
    review_comment = models.TextField("Комментарий модератора", blank=True)
    approved_article = models.OneToOneField(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_submission",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заявка на статью"
        verbose_name_plural = "Заявки на статьи"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Заявка статьи #{self.pk}: {self.title}"


class SubmissionImage(models.Model):
    submission = models.ForeignKey(
        ArticleSubmission,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        "Изображение",
        upload_to="article_submissions/%Y/%m/",
        validators=[validate_image_size],
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Изображение заявки"
        verbose_name_plural = "Изображения заявок"
        ordering = ("sort_order", "id")

    def __str__(self) -> str:
        return f"Изображение заявки #{self.submission_id}"


class ProductCategory(models.Model):
    name = models.CharField("Название", max_length=80, unique=True)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField("Название", max_length=140)
    slug = models.SlugField("Slug", max_length=180, unique=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField(
        "Цена",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ShopPreorder(models.Model):
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
        related_name="shop_preorders",
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="preorders",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="preorders",
    )
    desired_item = models.CharField("Желаемый товар", max_length=200, blank=True)
    quantity = models.PositiveIntegerField(
        "Количество",
        default=1,
        validators=[MinValueValidator(1)],
    )
    phone = models.CharField("Телефон", max_length=20, validators=[phone_validator])
    email = models.EmailField("Email", blank=True)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Предзаказ магазина"
        verbose_name_plural = "Предзаказы магазина"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Предзаказ #{self.pk}"


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
    article = models.ForeignKey(
        Article,
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
