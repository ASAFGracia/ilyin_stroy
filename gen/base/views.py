from urllib import request
from django.shortcuts import get_object_or_404
from .models import *
from .forms import *
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from .forms import ContactForm
from django.utils.timezone import now


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

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'base/add_product.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    categories = ProductCategory.objects.all()
    return render(request, 'base/product_list.html', {
        'products': products,
        'categories': categories,
    })

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, 'base/delete_product.html', {'product': product})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'base/edit_product.html', {'form': form, 'product': product})

def choose_form(request):
    form_type = request.GET.get('form_type')
    if form_type == 'product':
        return redirect('product_list')
    elif form_type == 'category':
        return redirect('category_list')
    return render(request, 'base/select_form.html')

def add_category(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = ProductCategoryForm()
    return render(request, 'base/add_category.html', {'form': form})

def category_list(request):
    categorys = ProductCategory.objects.all()
    return render(request, 'base/category_list.html', {'categorys': categorys})

def delete_category(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect('category_list')
    return render(request, 'base/delete_category.html', {'category': category})

def edit_category(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = ProductCategoryForm(instance=category)
    context = {
        'category': category,
    }
    return render(request, 'base/edit_category.html', {'form': form, 'category': category})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            print("Данные формы:", form.cleaned_data)
            return render(request, 'base/success_page.html')
    else:
        form = ContactForm()

    return render(request, 'base/index.html', {'form': form})

def success_page(request):
    render (request, 'base/success_page.html')

def current_month_categories(request):
    today = now()
    categories = ProductCategory.objects.filter(
        category_created_at__year=today.year,
        category_created_at__month=today.month
    )
    return render(request, 'base/current_month_categories.html', {'categories': categories})

def products_by_category(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'base/products_by_category.html', {
        'category': category,
        'products': products,
    })