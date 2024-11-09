from urllib import request
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.conf import settings
from django.shortcuts import render


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
