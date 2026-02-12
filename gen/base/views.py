from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import slugify

from .forms import (
    ArticleCreateForm,
    ArticleOrderForm,
    ArticleSubmissionForm,
    ContactForm,
    EmailAuthRequestForm,
    EmailAuthVerifyForm,
    FeedbackForm,
    OrderRequestForm,
    ProfileSettingsForm,
    ProfileUserForm,
    ShopPreorderForm,
    SubmissionReviewForm,
)
from .models import (
    Article,
    ArticleImage,
    ArticleSubmission,
    EmailAuthCode,
    OrderRequest,
    Product,
    ProductCategory,
    Profile,
    ShopPreorder,
    SubmissionImage,
)

User = get_user_model()
ORDER_EMAIL = settings.ORDER_RECIPIENT_EMAIL
OWNER_EMAIL = settings.OWNER_EMAIL.lower().strip()

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


def _is_owner(user) -> bool:
    return bool(user.is_authenticated and user.email and user.email.lower() == OWNER_EMAIL)


def _owner_or_404(request):
    if not _is_owner(request.user):
        raise Http404("Страница не найдена")


def _notify(subject: str, message: str, from_email: str | None = None) -> None:
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ORDER_EMAIL],
        fail_silently=False,
    )


def _get_or_create_user_by_email(email: str):
    normalized = email.strip().lower()
    user = User.objects.filter(email__iexact=normalized).first()
    if user:
        return user, False

    base = slugify(normalized.split("@")[0]) or "user"
    candidate = base
    i = 1
    while User.objects.filter(username=candidate).exists():
        i += 1
        candidate = f"{base}{i}"

    user = User.objects.create(username=candidate, email=normalized)
    user.set_unusable_password()
    user.save(update_fields=["password"])
    return user, True


def _save_article_images(article: Article, files) -> None:
    for idx, image in enumerate(files):
        ArticleImage.objects.create(article=article, image=image, sort_order=idx)


def _save_submission_images(submission: ArticleSubmission, files) -> None:
    for idx, image in enumerate(files):
        SubmissionImage.objects.create(submission=submission, image=image, sort_order=idx)


def auth_login_request(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("profile")

    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        request.session["auth_next"] = next_url

    if request.method == "POST":
        form = EmailAuthRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower().strip()
            _get_or_create_user_by_email(email)
            latest_code = (
                EmailAuthCode.objects.filter(email=email)
                .order_by("-created_at")
                .first()
            )
            if latest_code and (timezone.now() - latest_code.created_at).total_seconds() < 45:
                messages.info(request, "Код уже недавно отправлялся. Подождите 45 секунд.")
                request.session["pending_auth_email"] = email
                return redirect("auth_verify_code")
            try:
                _, code = EmailAuthCode.issue_code(
                    email=email,
                    requested_ip=request.META.get("REMOTE_ADDR"),
                    ttl_minutes=settings.AUTH_CODE_TTL_MINUTES,
                    max_attempts=settings.AUTH_CODE_MAX_ATTEMPTS,
                )
                _notify(
                    subject=f"Код входа в {settings.SITE_BRAND}",
                    message=(
                        f"Ваш код подтверждения: {code}\n"
                        f"Код действует {settings.AUTH_CODE_TTL_MINUTES} минут.\n"
                        "Если это были не вы, просто проигнорируйте письмо."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                )
                request.session["pending_auth_email"] = email
                messages.success(request, "Код отправлен на вашу почту.")
                return redirect("auth_verify_code")
            except Exception:
                messages.error(request, "Не удалось отправить код. Попробуйте позже.")
    else:
        form = EmailAuthRequestForm()

    return render(request, "base/auth_login_request.html", {"form": form})


def auth_verify_code(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("profile")

    pending_email = request.session.get("pending_auth_email", "").strip().lower()
    if not pending_email:
        messages.info(request, "Сначала запросите код входа.")
        return redirect("auth_login_request")

    if request.method == "POST":
        form = EmailAuthVerifyForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower().strip()
            code = form.cleaned_data["code"].strip()
            auth_code = (
                EmailAuthCode.objects.filter(email=email, is_used=False)
                .order_by("-created_at")
                .first()
            )
            if not auth_code or auth_code.is_expired():
                messages.error(request, "Код истек. Запросите новый код.")
                return redirect("auth_login_request")

            if auth_code.verify_code(code):
                user, _ = _get_or_create_user_by_email(email)
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                request.session.pop("pending_auth_email", None)
                next_url = request.session.pop("auth_next", None)
                messages.success(request, "Вы успешно вошли в аккаунт.")
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                ):
                    return redirect(next_url)
                return redirect("profile")

            messages.error(request, "Неверный код. Проверьте письмо и попробуйте снова.")
    else:
        form = EmailAuthVerifyForm(initial={"email": pending_email})

    active_code = (
        EmailAuthCode.objects.filter(email=pending_email, is_used=False)
        .order_by("-created_at")
        .first()
    )
    attempts_left = active_code.attempts_left if active_code else 0

    return render(
        request,
        "base/auth_verify_code.html",
        {
            "form": form,
            "pending_email": pending_email,
            "attempts_left": attempts_left,
        },
    )


def auth_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("home")


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            suggestions = form.cleaned_data["suggestions"]
            try:
                _notify("Новое предложение с сайта Mastersvarki", suggestions)
                messages.success(request, "Спасибо! Предложение отправлено.")
            except Exception:
                messages.error(request, "Не удалось отправить сообщение. Попробуйте позже.")
            return redirect("support")
    else:
        form = FeedbackForm()

    return render(request, "base/support.html", {"form": form})


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            fio = form.cleaned_data["fio"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
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

    return render(request, "base/index.html", {"form": form})


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
    selected_slug = request.GET.get("category", "").strip()
    categories = ProductCategory.objects.filter(is_active=True).order_by("name")
    products = Product.objects.filter(is_active=True).select_related("category")
    selected_category = None
    if selected_slug:
        selected_category = ProductCategory.objects.filter(slug=selected_slug, is_active=True).first()
        if selected_category:
            products = products.filter(category=selected_category)

    if request.method == "POST":
        preorder_form = ShopPreorderForm(request.POST)
        if preorder_form.is_valid():
            preorder = preorder_form.save(commit=False)
            if request.user.is_authenticated:
                preorder.user = request.user
            if preorder.product and not preorder.category:
                preorder.category = preorder.product.category
            preorder.save()
            try:
                _notify(
                    subject=f"Новый предзаказ магазина #{preorder.id}",
                    message=(
                        f"Пользователь: {preorder.user.email if preorder.user else '-'}\n"
                        f"Категория: {preorder.category.name if preorder.category else '-'}\n"
                        f"Товар: {preorder.product.name if preorder.product else '-'}\n"
                        f"Другой товар: {preorder.desired_item or '-'}\n"
                        f"Количество: {preorder.quantity}\n"
                        f"Телефон: {preorder.phone}\n"
                        f"Email: {preorder.email or '-'}\n\n"
                        f"Комментарий:\n{preorder.comment or '-'}"
                    ),
                )
                messages.success(request, "Предзаказ отправлен. Мы свяжемся с вами.")
            except Exception:
                messages.warning(request, "Предзаказ сохранен, но письмо не отправлено.")
            redirect_url = "shop"
            if selected_slug:
                redirect_url = f"{redirect('shop').url}?category={selected_slug}"
                return redirect(redirect_url)
            return redirect("shop")
        messages.error(request, "Проверьте корректность полей предзаказа.")
    else:
        initial = {}
        if request.user.is_authenticated:
            profile_obj, _ = Profile.objects.get_or_create(user=request.user)
            initial = {
                "phone": profile_obj.phone,
                "email": request.user.email,
            }
        preorder_form = ShopPreorderForm(initial=initial)

    return render(
        request,
        "base/shop_catalog.html",
        {
            "categories": categories,
            "products": products,
            "selected_category": selected_category,
            "preorder_form": preorder_form,
        },
    )


def articles(request):
    queryset = Article.objects.filter(is_published=True).prefetch_related("images")
    if _is_owner(request.user):
        queryset = Article.objects.all().prefetch_related("images")
    return render(
        request,
        "base/articles.html",
        {
            "articles": queryset,
            "can_create_articles": _is_owner(request.user),
        },
    )


def article_detail(request, slug: str):
    article = get_object_or_404(Article.objects.prefetch_related("images"), slug=slug)
    if not article.is_published and not _is_owner(request.user):
        raise Http404("Статья не опубликована")

    preview_only = not request.user.is_authenticated
    preview_text = article.content[:1200]

    if request.method == "POST":
        order_form = ArticleOrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.article = article
            order.contact_method = "phone"
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            try:
                _notify(
                    subject=f"Новая заявка по статье #{order.id}",
                    message=(
                        f"Статья: {article.title}\n"
                        f"Имя: {order.name}\n"
                        f"Телефон: {order.phone}\n"
                        f"Email: {order.email or '-'}\n\n"
                        f"Комментарий:\n{order.message or '-'}"
                    ),
                )
                messages.success(request, "Заявка по статье отправлена.")
            except Exception:
                messages.warning(request, "Заявка сохранена, но письмо не отправилось.")
            return redirect("article_detail", slug=article.slug)
        messages.error(request, "Проверьте корректность заявки.")
    else:
        initial = {}
        if request.user.is_authenticated:
            profile_obj, _ = Profile.objects.get_or_create(user=request.user)
            initial = {
                "name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
                "phone": profile_obj.phone,
            }
        order_form = ArticleOrderForm(initial=initial)

    return render(
        request,
        "base/article_detail.html",
        {
            "article": article,
            "preview_only": preview_only,
            "preview_text": preview_text,
            "order_form": order_form,
        },
    )


@login_required
@user_passes_test(_is_owner, login_url="auth_login_request")
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
@user_passes_test(_is_owner, login_url="auth_login_request")
def article_create(request):
    template_key = request.GET.get("template", "custom")
    preset = ARTICLE_TEMPLATE_PRESETS.get(template_key, {})

    if request.method == "POST":
        form = ArticleCreateForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            _save_article_images(article, form.cleaned_data.get("images", []))
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


@login_required
def article_submit_request(request):
    preview_data = None
    if request.method == "POST":
        form = ArticleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            if "preview" in request.POST:
                preview_data = {
                    "title": form.cleaned_data["title"],
                    "summary": form.cleaned_data["summary"],
                    "content": form.cleaned_data["content"],
                }
                messages.info(request, "Это предпросмотр. Для отправки нажмите 'Отправить на модерацию'.")
            else:
                submission = form.save(commit=False)
                submission.user = request.user
                submission.save()
                _save_submission_images(submission, form.cleaned_data.get("images", []))
                messages.success(request, "Заявка на статью отправлена на модерацию.")
                return redirect("profile")
    else:
        form = ArticleSubmissionForm()

    return render(
        request,
        "base/article_submit_request.html",
        {
            "form": form,
            "preview_data": preview_data,
        },
    )


@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)
    user_orders = OrderRequest.objects.filter(user=request.user).order_by("-created_at")[:10]
    user_preorders = ShopPreorder.objects.filter(user=request.user).order_by("-created_at")[:10]
    user_submissions = ArticleSubmission.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(
        request,
        "base/profile.html",
        {
            "user_orders": user_orders,
            "user_preorders": user_preorders,
            "user_submissions": user_submissions,
        },
    )


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
    article_slug = request.GET.get("article", "").strip()
    article = Article.objects.filter(slug=article_slug, is_published=True).first() if article_slug else None

    if request.method == "POST":
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            article_id = request.POST.get("article_id")
            if article_id:
                order.article_id = article_id
            elif article:
                order.article = article
            order.save()
            try:
                _notify(
                    subject=f"Новая заявка на Mastersvarki #{order.id}",
                    message=(
                        f"Имя: {order.name}\n"
                        f"Телефон: {order.phone}\n"
                        f"Email: {order.email or '-'}\n"
                        f"Способ связи: {order.get_contact_method_display()}\n"
                        f"Статья: {order.article.title if order.article else '-'}\n\n"
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
    return render(request, "base/order_request.html", {"form": form, "article": article})


@login_required
@user_passes_test(_is_owner, login_url="auth_login_request")
def owner_dashboard(request):
    submissions = ArticleSubmission.objects.select_related("user", "approved_article").prefetch_related("images")
    users = User.objects.order_by("-date_joined")[:300]
    orders = OrderRequest.objects.select_related("user", "article").order_by("-created_at")[:200]
    preorders = ShopPreorder.objects.select_related("user", "category", "product").order_by("-created_at")[:200]
    review_form = SubmissionReviewForm()
    return render(
        request,
        "base/owner_dashboard.html",
        {
            "submissions": submissions,
            "users": users,
            "orders": orders,
            "preorders": preorders,
            "review_form": review_form,
        },
    )


@login_required
@user_passes_test(_is_owner, login_url="auth_login_request")
def owner_submission_approve(request, submission_id: int):
    if request.method != "POST":
        return redirect("owner_dashboard")

    submission = get_object_or_404(ArticleSubmission, pk=submission_id)
    form = SubmissionReviewForm(request.POST)
    comment = ""
    if form.is_valid():
        comment = form.cleaned_data.get("review_comment", "")

    if submission.status == ArticleSubmission.STATUS_APPROVED and submission.approved_article:
        messages.info(request, "Эта заявка уже одобрена.")
        return redirect("owner_dashboard")

    article = Article.objects.create(
        template_key="custom",
        title=submission.title,
        summary=submission.summary,
        content=submission.content,
        is_published=True,
        author=request.user,
    )
    for idx, submission_image in enumerate(submission.images.all()):
        ArticleImage.objects.create(
            article=article,
            image=submission_image.image.name,
            sort_order=idx,
        )

    submission.status = ArticleSubmission.STATUS_APPROVED
    submission.reviewer = request.user
    submission.review_comment = comment
    submission.approved_article = article
    submission.save(
        update_fields=[
            "status",
            "reviewer",
            "review_comment",
            "approved_article",
            "updated_at",
        ]
    )

    messages.success(request, "Заявка одобрена и опубликована как статья.")
    return redirect("owner_dashboard")


@login_required
@user_passes_test(_is_owner, login_url="auth_login_request")
def owner_submission_reject(request, submission_id: int):
    if request.method != "POST":
        return redirect("owner_dashboard")

    submission = get_object_or_404(ArticleSubmission, pk=submission_id)
    form = SubmissionReviewForm(request.POST)
    comment = ""
    if form.is_valid():
        comment = form.cleaned_data.get("review_comment", "")

    submission.status = ArticleSubmission.STATUS_REJECTED
    submission.reviewer = request.user
    submission.review_comment = comment
    submission.save(update_fields=["status", "reviewer", "review_comment", "updated_at"])
    messages.success(request, "Заявка отклонена.")
    return redirect("owner_dashboard")
