from django import forms


class ContactForm(forms.Form):
    fio = forms.CharField(label="ФИО", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Введите ФИО'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'placeholder': 'Введите email'}))
    message = forms.CharField(label="Сообщение", widget=forms.Textarea(attrs={'placeholder': 'Отправьте нам сообщение'}))
