from django import forms
from django.contrib.auth.models import User

from .models import Article, OrderRequest, Profile, phone_validator


class ContactForm(forms.Form):
    fio = forms.CharField(
        label="Имя",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Введите имя",
                "class": "inputf1",
                "id": "fio",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Введите email",
                "class": "inputf1",
                "id": "email",
            }
        ),
    )
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Опишите ваш вопрос",
                "class": "inputf1",
                "id": "txt",
                "rows": 4,
                "cols": 50,
            }
        ),
    )


class FeedbackForm(forms.Form):
    suggestions = forms.CharField(
        label="Ваши предложения",
        widget=forms.Textarea(
            attrs={
                "class": "inputfsup",
                "id": "predi",
                "rows": 4,
                "cols": 50,
                "placeholder": "Напишите нам",
            }
        ),
        max_length=1000,
    )


class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Фамилия"}
            ),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }


class ProfileSettingsForm(forms.ModelForm):
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        validators=[phone_validator],
        required=False,
        widget=forms.TextInput(
            attrs={"class": "inputf1", "placeholder": "+375 (xx) xxx-xx-xx"}
        ),
    )

    class Meta:
        model = Profile
        fields = ("nickname", "phone")
        widgets = {
            "nickname": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Ваш никнейм"}
            ),
        }
        labels = {
            "nickname": "Никнейм",
        }


class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("template_key", "title", "summary", "content", "is_published")
        widgets = {
            "template_key": forms.Select(attrs={"class": "inputf1"}),
            "title": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Заголовок статьи"}
            ),
            "summary": forms.Textarea(
                attrs={"class": "inputf1", "rows": 3, "placeholder": "Краткое описание"}
            ),
            "content": forms.Textarea(
                attrs={"class": "inputf1", "rows": 16, "placeholder": "Текст статьи"}
            ),
            "is_published": forms.CheckboxInput(attrs={"class": "checkf1"}),
        }
        labels = {
            "template_key": "Шаблон",
            "title": "Заголовок",
            "summary": "Краткое описание",
            "content": "Содержимое",
            "is_published": "Опубликовать сразу",
        }


class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ("name", "phone", "email", "contact_method", "message")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Как к вам обращаться"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "+375 (xx) xxx-xx-xx"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "inputf1", "placeholder": "email (необязательно)"}
            ),
            "contact_method": forms.Select(attrs={"class": "inputf1"}),
            "message": forms.Textarea(
                attrs={
                    "class": "inputf1",
                    "rows": 5,
                    "placeholder": "Опишите задачу, адрес, сроки",
                }
            ),
        }
        labels = {
            "name": "Имя",
            "phone": "Телефон",
            "email": "Email",
            "contact_method": "Предпочтительный способ связи",
            "message": "Комментарий к заказу",
        }
