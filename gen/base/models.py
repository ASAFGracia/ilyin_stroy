from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from django.db import models
import random


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    status = models.CharField(
        max_length=10, choices=[('pending', 'На проверке'), ('approved', 'Одобрено'), ('rejected', 'Отклонено')],
        default='pending'
    )

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.pk:  # Только при первом создании статьи
            self.status = 'pending'  # Статья сохраняется как "На проверке"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='articles/', verbose_name="Изображение")
    position = models.PositiveIntegerField(verbose_name="Позиция в тексте")


class ArticleWriterRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Заявка от {self.user.username} на написание статьи"


class AdminLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Ссылаемся на кастомную модель пользователя
    action_time = models.DateTimeField(auto_now_add=True)
    # другие поля

    def __str__(self):
        return f"Action by {self.user} at {self.action_time}"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    unique_id = models.CharField(max_length=7, unique=True)  # 7-значный ID
    is_verified = models.BooleanField(default=False)  # Подтверждение почты
    verification_code = models.CharField(max_length=6, blank=True, null=True)  # Код подтверждения
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.unique_id})"

    # def save(self, *args, **kwargs):
    #     if not self.unique_id:
    #         self.unique_id = self.generate_unique_id()
    #     super().save(*args, **kwargs)

    # @staticmethod
    # def generate_unique_id():
    #     while True:
    #         new_id = str(random.randint(1000000, 9999999))
    #         if not CustomUser.objects.filter(unique_id=new_id).exists():
    #             return new_id

