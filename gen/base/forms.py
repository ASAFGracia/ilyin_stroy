from django import forms


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