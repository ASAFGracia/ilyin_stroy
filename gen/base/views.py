from urllib import request

from django.shortcuts import render


def index(request):
    return render (request, "base/index.html")

def fundament(request):
    return render (request, "base/fundament.html")

def onas(request):
    return render (request, "base/onas.html")

def contacts(request):
    return render (request, "base/contacts.html")
