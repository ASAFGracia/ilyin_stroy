from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import Article, ArticleImage
from .models import CustomUser
from django import forms
from .models import ArticleWriterRequest
import random

class ContactForm(forms.Form):
    fio = forms.CharField(
        label="ФИО",
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите ФИО',
            'class': 'inputf1',
            'id': 'fio',
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите email',
            'class': 'inputf1',
            'id': 'email',
        })
    )
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={
            'placeholder': 'Отправьте нам сообщение',
            'class': 'inputf1',
            'id': 'txt',
            'rows': 4,
            'cols': 50,
        })
    )


class FeedbackForm(forms.Form):
    suggestions = forms.CharField(
        label="Ваши предложения",
        widget=forms.Textarea(attrs={
            'class': 'inputfsup',
            'id': 'predi',
            'rows': 4,
            'cols': 50,
            'placeholder': 'Напишите нам',
        }),
        max_length=1000,
    )


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'new-art-title',
                'placeholder': 'Введите заголовок статьи'
            }),
            'content': forms.Textarea(attrs={
                'class': 'new-art-content',
                'placeholder': 'Введите содержание статьи',
                'rows': 5
            }),
            'slug': forms.TextInput(attrs={
                'class': 'new-art-slug',
                'placeholder': 'Введите URL'
            }),
        }

ArticleImageFormSet = inlineformset_factory(
    parent_model=Article,
    model=ArticleImage,
    fields=('image', 'position'),
    extra=1,          # Количество дополнительных пустых форм
    can_delete=True   # Возможность удалять изображения, если потребуется
)


class ArticleWriterRequestForm(forms.ModelForm):
    class Meta:
        model = ArticleWriterRequest
        fields = []


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    unique_id = forms.CharField(
        max_length=7,
        required=False,  # Убираем обязательность, так как будет авто-генерация
        widget=forms.TextInput(attrs={"placeholder": "Число от 1 до 9999999"})
    )
    random_unique_id = forms.BooleanField(
        required=False,
        initial=False,
        label="Сгенерировать ID автоматически"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'unique_id', 'random_unique_id', 'password1', 'password2']
        labels = {
            "username": "Имя пользователя",
            "email": "Email",
            "unique_id": "Уникальный идентификатор",
            "random_unique_id": "Сгенерировать ID автоматически",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }

    def clean_unique_id(self):
        unique_id = self.cleaned_data.get("unique_id")
        random_unique = self.cleaned_data.get("random_unique_id")

        if random_unique:
            existing_ids = set(CustomUser.objects.values_list("unique_id", flat=True))
            available_ids = set(range(1, 10000000)) - existing_ids
            if available_ids:
                return str(random.choice(list(available_ids)))
            raise forms.ValidationError("Не удалось сгенерировать ID. Все заняты.")

        if not unique_id:
            raise forms.ValidationError("Введите ID или включите автогенерацию.")

        if not unique_id.isdigit() or not (1 <= int(unique_id) <= 9999999):
            raise forms.ValidationError("ID должен быть числом от 1 до 9999999.")

        if CustomUser.objects.filter(unique_id=unique_id).exists():
            raise forms.ValidationError("Этот ID уже занят. Выберите другой.")

        return unique_id


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))