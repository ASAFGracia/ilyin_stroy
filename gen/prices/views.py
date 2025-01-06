from django.shortcuts import render, redirect

def santehnika(request):
    return render (request, "prices/santehnika.html")
