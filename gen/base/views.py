from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ArticleCreateForm,
    ContactForm,
    FeedbackForm,
    OrderRequestForm,
    ProfileSettingsForm,
    ProfileUserForm,
)
from .models import Article, OrderRequest, Profile

ORDER_EMAIL = settings.ORDER_RECIPIENT_EMAIL

ARTICLE_TEMPLATE_PRESETS = {
    "walls": {
        "title": "Наружные и внутренние стены",
        "summary": "Базовые решения по стенам и перегородкам: материалы, этапы, контроль качества.",
        "content": (
            "## Для чего нужна эта статья\n"
            "Кратко объясните, в каких случаях клиенту нужен этот вид работ.\n\n"
            "## Какие материалы используем\n"
            "- Газобетон/кирпич/каркас\n"
            "- Растворы и крепеж\n"
            "- Утепление и пароизоляция\n\n"
            "## Этапы работ\n"
            "1. Подготовка основания и разметка.\n"
            "2. Монтаж/кладка стен.\n"
            "3. Контроль геометрии.\n"
            "4. Черновая/финишная отделка.\n\n"
            "## Сроки и стоимость\n"
            "Опишите, от чего зависит финальная цена и сроки.\n\n"
            "## Что получает клиент\n"
            "Укажите гарантию, аккуратность работ, фотоотчеты."
        ),
    },
    "lower_floor": {
        "title": "Полы нижнего этажа",
        "summary": "Полы по грунту, утепление, гидроизоляция и подготовка под финишные покрытия.",
        "content": (
            "## Когда требуется устройство пола нижнего этажа\n"
            "Опишите типовые задачи: новый дом, реконструкция, утепление.\n\n"
            "## Что входит в работы\n"
            "- Подготовка основания\n"
            "- Гидроизоляция\n"
            "- Утепление\n"
            "- Черновая стяжка\n"
            "- Подготовка под чистовой пол\n\n"
            "## Этапы и контроль\n"
            "Укажите ключевые этапы и контрольные точки качества.\n\n"
            "## Практические рекомендации\n"
            "Добавьте советы по эксплуатации и выбору материалов."
        ),
    },
    "drainage": {
        "title": "Дренажная система и коммуникации",
        "summary": "Как защищаем фундамент и участок от воды: дренаж, ливневка, отвод.",
        "content": (
            "## Зачем нужен дренаж\n"
            "Кратко о рисках подтопления и разрушения конструкций.\n\n"
            "## Что проектируем\n"
            "- Кольцевой/пристенный дренаж\n"
            "- Ливневый отвод\n"
            "- Колодцы и ревизии\n\n"
            "## Монтаж\n"
            "Опишите последовательность: земляные работы, уклон, трубы, щебень, геотекстиль.\n\n"
            "## Результат\n"
            "Подчеркните эффект для долговечности дома."
        ),
    },
}


def _notify(subject: str, message: str, from_email: str | None = None) -> None:
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ORDER_EMAIL],
        fail_silently=False,
    )


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            suggestions = form.cleaned_data['suggestions']
            try:
                _notify("Новое предложение с сайта Mastersvarki", suggestions)
                messages.success(request, "Спасибо! Предложение отправлено.")
            except Exception:
                messages.error(request, "Не удалось отправить сообщение. Попробуйте позже.")
            return redirect("support")
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
            try:
                _notify(
                    subject=f"Новое сообщение на Mastersvarki от {fio}",
                    message=f"Email: {email}\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                )
                messages.success(request, "Спасибо! Мы получили ваше сообщение.")
            except Exception:
                messages.error(request, "Не удалось отправить сообщение. Попробуйте позже.")
            return redirect("home")

    else:
        form = ContactForm()

    return render(request, 'base/index.html', {'form': form})



def index(request):
    form = ContactForm()
    return render(request, "base/index.html", {"form": form})

def fundament(request):
    return render(request, "base/fundament.html")

def installation(request):
    return render(request, "base/installation.html")

def service(request):
    return render(request, "base/service.html")

def contacts(request):
    return render(request, "base/contacts.html")

def support(request):
    form = FeedbackForm()
    return render(request, "base/support.html", {"form": form})

def sistemaotopleniya(request):
    return render(request, "base/sistema-otopleniya.html")

def shop(request):
    return render(request, "base/shop.html")


def articles(request):
    if request.user.is_staff:
        queryset = Article.objects.all()
    else:
        queryset = Article.objects.filter(is_published=True)
    return render(request, "base/articles.html", {"articles": queryset})


def article_detail(request, slug: str):
    article = get_object_or_404(Article, slug=slug)
    if not article.is_published and not request.user.is_staff:
        raise Http404("Статья не опубликована")
    return render(request, "base/article_detail.html", {"article": article})


@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)
    user_orders = OrderRequest.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(request, "base/profile.html", {"user_orders": user_orders})


@login_required
def profile_settings(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        user_form = ProfileUserForm(request.POST, instance=request.user)
        profile_form = ProfileSettingsForm(request.POST, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Профиль обновлен.")
            return redirect("profile")
        messages.error(request, "Проверьте корректность введенных данных.")
    else:
        user_form = ProfileUserForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=profile_obj)
    return render(
        request,
        "base/profile_settings.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


def order_request(request):
    if request.method == "POST":
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            try:
                _notify(
                    subject=f"Новая заявка на Mastersvarki #{order.id}",
                    message=(
                        f"Имя: {order.name}\n"
                        f"Телефон: {order.phone}\n"
                        f"Email: {order.email or '-'}\n"
                        f"Способ связи: {order.get_contact_method_display()}\n\n"
                        f"Комментарий:\n{order.message or '-'}"
                    ),
                )
                messages.success(request, "Заявка отправлена. Мы свяжемся с вами.")
            except Exception:
                messages.warning(
                    request,
                    "Заявка сохранена, но email пока не отправился. Мы обработаем ее вручную.",
                )
            return redirect("orders")
        messages.error(request, "Проверьте корректность введенных данных.")
    else:
        initial = {}
        if request.user.is_authenticated:
            profile_obj, _ = Profile.objects.get_or_create(user=request.user)
            initial = {
                "name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
                "phone": profile_obj.phone,
            }
        form = OrderRequestForm(initial=initial)
    return render(request, "base/order_request.html", {"form": form})


@login_required
@user_passes_test(lambda user: user.is_staff)
def article_templates(request):
    templates = [
        {
            "key": key,
            "title": payload["title"],
            "summary": payload["summary"],
            "create_url": f"/articles/new/?template={key}",
        }
        for key, payload in ARTICLE_TEMPLATE_PRESETS.items()
    ]
    return render(request, "base/article_templates.html", {"templates": templates})


@login_required
@user_passes_test(lambda user: user.is_staff)
def article_create(request):
    template_key = request.GET.get("template", "custom")
    preset = ARTICLE_TEMPLATE_PRESETS.get(template_key, {})
    if request.method == "POST":
        form = ArticleCreateForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Статья сохранена.")
            return redirect("article_detail", slug=article.slug)
    else:
        form = ArticleCreateForm(
            initial={
                "template_key": template_key if template_key in ARTICLE_TEMPLATE_PRESETS else "custom",
                "title": preset.get("title", ""),
                "summary": preset.get("summary", ""),
                "content": preset.get("content", ""),
                "is_published": True,
            }
        )
    return render(request, "base/article_create.html", {"form": form, "template_key": template_key})
