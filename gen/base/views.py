import random

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ArticleForm, ArticleImageFormSet
from .forms import ArticleWriterRequestForm
from .forms import ContactForm, FeedbackForm
from .forms import RegistrationForm
from .models import Article
from .models import CustomUser, ArticleWriterRequest


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


@login_required
def article_list(request):
    articles = Article.objects.all().order_by('-created_at')
    approved_requests = ArticleWriterRequest.objects.filter(user=request.user, status='approved')

    # Передаем одобренные заявки в шаблон
    return render(request, 'base/article_list.html', {
        'articles': articles,
        'approved_requests': approved_requests,
    })

@login_required
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'base/article_detail.html', {'article': article})

@login_required
def create_article(request):
    if request.method == 'POST':
        article_form = ArticleForm(request.POST)
        image_formset = ArticleImageFormSet(request.POST, request.FILES)

        if article_form.is_valid() and image_formset.is_valid():
            # Получаем текущего пользователя
            user = request.user

            # Создаем статью и устанавливаем автора
            if user.is_approved:
                article = article_form.save(commit=False)
                article.author = user  # Устанавливаем текущего пользователя как автора
                article.save()

                # Сохраняем изображения, привязывая их к статье
                images = image_formset.save(commit=False)
                for img in images:
                    img.article = article
                    img.save()

                # Обработка удаления изображений
                for form in image_formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()

                return redirect('article_list')  # Перенаправление, например, на страницу со списком статей

            # Проверяем, существует ли пользователь в базе данных
            return render(request, 'base/error.html', {'message': 'Your account is not approved yet.'})

    else:
        article_form = ArticleForm()
        image_formset = ArticleImageFormSet()

    context = {
        'article_form': article_form,
        'image_formset': image_formset,
    }
    return render(request, 'base/create_article.html', context)



@login_required
def request_to_write_article(request):
    if request.method == 'POST':
        form = ArticleWriterRequestForm(request.POST)
        if form.is_valid():
            # Устанавливаем пользователя как автора заявки
            request_to_write = form.save(commit=False)
            request_to_write.user = request.user
            request_to_write.save()
            return redirect('article_list')  # Перенаправление на список статей

    else:
        form = ArticleWriterRequestForm()

    return render(request, 'base/request_article_writer.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def approve_article_writer(request, pk):
    request_to_approve = get_object_or_404(ArticleWriterRequest, pk=pk)
    request_to_approve.status = 'approved'
    request_to_approve.save()
    return redirect('article_list')  # Можно перенаправить на страницу со списком статей


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Пока не подтверждён
            user.verification_code = str(random.randint(100000, 999999))  # Код подтверждения
            user.save()

            print(f"✅ Пользователь {user.username} успешно сохранён в БД!")  # Логируем процесс

            send_mail(
                "Подтверждение регистрации",
                f"Ваш код подтверждения: {user.verification_code}",
                "noreply@ilyin-stroy.xyz",
                [user.email],
                fail_silently=False,
            )

            request.session["user_id"] = user.id
            return redirect("verify_email")
        else:
            print("❌ Ошибка валидации формы:", form.errors)  # Логируем ошибки

    else:
        form = RegistrationForm()
    return render(request, "base/register.html", {"form": form})


def verify_email(request):
    if request.method == "POST":
        code = request.POST.get("code")
        user_id = request.session.get("user_id")
        user = CustomUser.objects.get(id=user_id)

        if user.verification_code == code:  # Теперь поле точно есть!
            user.is_active = True
            user.is_verified = True
            user.verification_code = None  # Очищаем код после подтверждения
            user.save()
            login(request, user)
            return redirect("home")  # После подтверждения — на главную

    return render(request, "base/verify_email.html")


@login_required
def profile_view(request):
    user = request.user  # Получаем текущего пользователя
    writer_request = ArticleWriterRequest.objects.filter(user=user).first()  # Ищем заявку на написание статьи, если она есть
    return render(request, 'base/profile.html', {'user': user, 'writer_request': writer_request})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profile")  # После входа — в профиль
        else:
            return render(request, "base/login.html", {"error": "Неверные данные!"})

    return render(request, "base/login.html")

def logout_view(request):
    logout(request)
    return redirect('home')  # Перенаправление на главную страницу