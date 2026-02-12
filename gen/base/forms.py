from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    AdminEmailAccess,
    Article,
    ArticleSubmission,
    OrderRequest,
    Product,
    ProductCategory,
    Profile,
    ShopPreorder,
    phone_validator,
)


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


def _article_limits() -> tuple[int, int]:
    max_symbols = int(getattr(settings, "ARTICLE_MAX_CONTENT_LENGTH", 20000))
    max_images = int(getattr(settings, "ARTICLE_MAX_IMAGES", 7))
    return max_symbols, max_images


def _max_image_bytes() -> int:
    mb = int(getattr(settings, "ARTICLE_IMAGE_MAX_MB", 10))
    return mb * 1024 * 1024


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


class EmailAuthRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "inputf1",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )


class EmailAuthVerifyForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    code = forms.RegexField(
        label="Код из письма",
        regex=r"^\d{6}$",
        error_messages={"invalid": "Введите 6-значный код."},
        widget=forms.TextInput(
            attrs={
                "class": "inputf1",
                "placeholder": "123456",
                "inputmode": "numeric",
                "maxlength": "6",
            }
        ),
    )


class TelegramAuthRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "inputf1",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )
    chat_id = forms.IntegerField(
        label="Ваш Telegram chat id",
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "inputf1",
                "placeholder": "Например: 8507895419",
                "inputmode": "numeric",
            }
        ),
    )


class TelegramAuthVerifyForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    chat_id = forms.IntegerField(widget=forms.HiddenInput())
    code = forms.RegexField(
        label="Код из Telegram",
        regex=r"^\d{6}$",
        error_messages={"invalid": "Введите 6-значный код."},
        widget=forms.TextInput(
            attrs={
                "class": "inputf1",
                "placeholder": "123456",
                "inputmode": "numeric",
                "maxlength": "6",
            }
        ),
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
    images = forms.FileField(
        required=False,
        widget=MultiFileInput(
            attrs={
                "class": "inputf1",
                "accept": "image/*",
            }
        ),
        help_text="До 7 изображений, каждое не больше 10 MB.",
    )

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
                attrs={
                    "class": "inputf1",
                    "rows": 18,
                    "placeholder": "Текст статьи. Используйте абзацы, списки и отступы.",
                }
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

    def clean_content(self):
        content = self.cleaned_data["content"]
        max_symbols, _ = _article_limits()
        if len(content) > max_symbols:
            raise ValidationError(f"Слишком длинный текст. Максимум {max_symbols} символов.")
        return content

    def clean_images(self):
        files = self.files.getlist("images")
        _, max_images = _article_limits()
        max_bytes = _max_image_bytes()
        if len(files) > max_images:
            raise ValidationError(f"Можно загрузить не более {max_images} изображений.")
        for image in files:
            if image.size > max_bytes:
                raise ValidationError("Каждое изображение должно быть не больше 10 MB.")
        return files


class ArticleSubmissionForm(forms.ModelForm):
    images = forms.FileField(
        required=False,
        widget=MultiFileInput(
            attrs={
                "class": "inputf1",
                "accept": "image/*",
            }
        ),
        help_text="До 7 изображений, каждое не больше 10 MB.",
    )

    class Meta:
        model = ArticleSubmission
        fields = ("title", "summary", "content")
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Заголовок будущей статьи"}
            ),
            "summary": forms.Textarea(
                attrs={"class": "inputf1", "rows": 3, "placeholder": "Кратко о статье"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "inputf1",
                    "rows": 16,
                    "placeholder": "Полный текст. Можно использовать абзацы и списки.",
                }
            ),
        }
        labels = {
            "title": "Заголовок",
            "summary": "Краткое описание",
            "content": "Текст статьи",
        }

    def clean_content(self):
        content = self.cleaned_data["content"]
        max_symbols, _ = _article_limits()
        if len(content) > max_symbols:
            raise ValidationError(f"Слишком длинный текст. Максимум {max_symbols} символов.")
        return content

    def clean_images(self):
        files = self.files.getlist("images")
        _, max_images = _article_limits()
        max_bytes = _max_image_bytes()
        if len(files) > max_images:
            raise ValidationError(f"Можно загрузить не более {max_images} изображений.")
        for image in files:
            if image.size > max_bytes:
                raise ValidationError("Каждое изображение должно быть не больше 10 MB.")
        return files


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


class ArticleOrderForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ("name", "phone", "email", "message")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Ваше имя"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "+375 (xx) xxx-xx-xx"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "inputf1", "placeholder": "Email (необязательно)"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "inputf1",
                    "rows": 4,
                    "placeholder": "Какая услуга нужна по этой статье",
                }
            ),
        }
        labels = {
            "name": "Имя",
            "phone": "Телефон",
            "email": "Email",
            "message": "Комментарий",
        }


class ShopPreorderForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Выберите категорию",
        widget=forms.Select(attrs={"class": "inputf1"}),
        label="Категория",
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        required=False,
        empty_label="Выберите товар (необязательно)",
        widget=forms.Select(attrs={"class": "inputf1"}),
        label="Товар",
    )

    class Meta:
        model = ShopPreorder
        fields = ("category", "product", "desired_item", "quantity", "phone", "email", "comment")
        widgets = {
            "desired_item": forms.TextInput(
                attrs={
                    "class": "inputf1",
                    "placeholder": "Если товара нет в списке, напишите его название",
                }
            ),
            "quantity": forms.NumberInput(attrs={"class": "inputf1", "min": "1"}),
            "phone": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "+375 (xx) xxx-xx-xx"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "inputf1", "placeholder": "Email (необязательно)"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "inputf1",
                    "rows": 4,
                    "placeholder": "Комментарий к предзаказу",
                }
            ),
        }
        labels = {
            "desired_item": "Нужен другой товар",
            "quantity": "Количество",
            "phone": "Телефон",
            "email": "Email",
            "comment": "Комментарий",
        }

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        product = cleaned_data.get("product")
        desired_item = (cleaned_data.get("desired_item") or "").strip()

        if not product and not desired_item:
            raise ValidationError("Выберите товар из списка или укажите, что нужно привезти под заказ.")

        if product and category and product.category_id != category.id:
            raise ValidationError("Выбранный товар не относится к указанной категории.")

        cleaned_data["desired_item"] = desired_item
        return cleaned_data


class SubmissionReviewForm(forms.Form):
    review_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "inputf1",
                "rows": 3,
                "placeholder": "Комментарий к решению (необязательно)",
            }
        ),
        label="Комментарий",
    )


class AdminEmailAccessForm(forms.ModelForm):
    class Meta:
        model = AdminEmailAccess
        fields = ("email", "note")
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "inputf1", "placeholder": "admin@example.com"}
            ),
            "note": forms.TextInput(
                attrs={"class": "inputf1", "placeholder": "Комментарий (необязательно)"}
            ),
        }
        labels = {
            "email": "Email администратора",
            "note": "Комментарий",
        }


class OrderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=OrderRequest.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "inputf1"}),
        label="Статус",
    )


class PreorderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=ShopPreorder.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "inputf1"}),
        label="Статус",
    )
