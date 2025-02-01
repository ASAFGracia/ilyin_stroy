from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import Article, ArticleImage
from .models import CustomUser
from django import forms
from .models import ArticleWriterRequest


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
        fields = ['status']
        widgets = {
            'status': forms.HiddenInput(attrs={'value': 'pending'}),
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    unique_id = forms.CharField(max_length=7, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'unique_id', 'password1', 'password2']

    def clean_unique_id(self):
        unique_id = self.cleaned_data['unique_id']
        if CustomUser.objects.filter(unique_id=unique_id).exists():
            raise forms.ValidationError("Этот ID уже занят. Выберите другой.")
        return unique_id

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Этот никнейм уже занят. Выберите другой.")
        return username

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))