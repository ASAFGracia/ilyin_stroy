from urllib import request
from django.shortcuts import render, redirect
from .forms import ContactForm, FeedbackForm
from django.core.mail import send_mail
from django.conf import settings


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            suggestions = form.cleaned_data['suggestions']
            send_mail(
                'Новое предложение с сайта',
                suggestions,
                settings.DEFAULT_FROM_EMAIL,
                ['ilyinstroy@gmail.com'],
            )
            return redirect ('/?success=1')
    else:
        form = FeedbackForm()

    return render(request, 'base/support.html', {'form': form})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            fio = form.cleaned_data['fio']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            send_mail(
                subject=f"Новое сообщение от {fio} с адресом {email}",
                message=message,
                from_email=email,
                recipient_list=['ilyinstroy@gmail.com'],
            )
            form = ContactForm()
            return redirect ('obout-us/?success=1')

    else:
        form = ContactForm()

    return render(request, 'base/index.html', {'form': form})



def index(request):
    return render (request, "base/index.html")

def fundament(request):
    return render (request, "base/fundament.html")

def onas(request):
    return render (request, "base/onas.html")

def contacts(request):
    return render (request, "base/contacts.html")

def support(request):
    return render (request, "base/support.html")

def sistemaotopleniya(request):
    return render (request, "base/sistema-otopleniya.html")