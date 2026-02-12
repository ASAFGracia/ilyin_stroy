from __future__ import annotations

import time
from typing import Any

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from base.access import normalize_email
from base.models import AdminEmailAccess, OrderRequest, ShopPreorder, TelegramAuthCode
from base.telegram import get_admin_chat_ids, send_telegram_message


HELP_TEXT = (
    "Команды:\n"
    "/help - помощь\n"
    "/myid - показать chat id\n"
    "/stats - сводка\n"
    "/orders [N] - последние заявки\n"
    "/order <id> - детали заявки\n"
    "/set_order <id> <new|in_progress|done>\n"
    "/preorders [N] - последние предзаказы\n"
    "/preorder <id> - детали предзаказа\n"
    "/set_preorder <id> <new|in_progress|done>\n"
    "/admins - активные админы\n"
    "/grant <email> - выдать админ-доступ\n"
    "/revoke <email> - отключить админ-доступ"
)

ORDER_STATUS_KEYS = {item[0] for item in OrderRequest.STATUS_CHOICES}
PREORDER_STATUS_KEYS = {item[0] for item in ShopPreorder.STATUS_CHOICES}
User = get_user_model()


class Command(BaseCommand):
    help = "Telegram bot polling for admin order processing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Read one polling cycle and exit",
        )
        parser.add_argument(
            "--poll-timeout",
            type=int,
            default=25,
            help="Telegram long-poll timeout in seconds",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=1.5,
            help="Sleep delay between cycles",
        )

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN.strip()
        if not token:
            raise CommandError("TELEGRAM_BOT_TOKEN is not configured")

        self.once = bool(options["once"])
        self.poll_timeout = max(1, int(options["poll_timeout"]))
        self.sleep = max(0.2, float(options["sleep"]))
        self.offset = self._get_start_offset()

        self.stdout.write(
            self.style.SUCCESS(
                f"Telegram bot polling started (timeout={self.poll_timeout}s, offset={self.offset})."
            )
        )

        while True:
            try:
                updates = self._get_updates(offset=self.offset, timeout=self.poll_timeout)
                for update in updates:
                    update_id = int(update.get("update_id", 0))
                    if update_id:
                        self.offset = max(self.offset, update_id + 1)
                    self._handle_update(update)
                if self.once:
                    break
                time.sleep(self.sleep)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Telegram bot polling interrupted by user."))
                break
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(f"Telegram bot loop error: {exc}"))
                if self.once:
                    raise
                time.sleep(max(self.sleep, 2.0))

        self.stdout.write(self.style.SUCCESS("Telegram bot polling stopped."))

    def _api_url(self, method: str) -> str:
        token = settings.TELEGRAM_BOT_TOKEN.strip()
        return f"https://api.telegram.org/bot{token}/{method}"

    def _get_start_offset(self) -> int:
        updates = self._get_updates(offset=None, timeout=1)
        if not updates:
            return 0
        return int(max(item.get("update_id", 0) for item in updates)) + 1

    def _get_updates(self, offset: int | None, timeout: int) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "timeout": timeout,
            "allowed_updates": ["message", "edited_message"],
        }
        if offset:
            payload["offset"] = offset

        response = requests.get(self._api_url("getUpdates"), params=payload, timeout=timeout + 10)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description", "Telegram getUpdates failed"))
        return data.get("result", [])

    def _handle_update(self, update: dict[str, Any]) -> None:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        chat = message.get("chat") or {}
        chat_id = str(chat.get("id", "")).strip()
        if not chat_id:
            return

        text = (message.get("text") or "").strip()
        if not text:
            return

        if text.startswith("/"):
            self._handle_command(chat_id, text)

    def _is_admin_chat(self, chat_id: str) -> bool:
        configured = {str(item).strip() for item in get_admin_chat_ids() if str(item).strip()}
        if chat_id in configured:
            return True

        try:
            chat_id_int = int(chat_id)
        except ValueError:
            return False

        admin_emails = {normalize_email(settings.OWNER_EMAIL)}
        admin_emails.update(
            AdminEmailAccess.objects.filter(is_active=True).values_list("email", flat=True)
        )
        admin_emails.discard("")
        if not admin_emails:
            return False

        return TelegramAuthCode.objects.filter(
            chat_id=chat_id_int,
            email__in=admin_emails,
            is_used=True,
        ).exists()

    def _send(self, chat_id: str, text: str) -> None:
        ok, err = send_telegram_message(chat_id, text)
        if not ok:
            self.stderr.write(self.style.ERROR(f"Failed sending to chat {chat_id}: {err}"))

    def _handle_command(self, chat_id: str, raw_text: str) -> None:
        chunks = raw_text.split()
        if not chunks:
            return

        command = chunks[0].split("@")[0].lower()
        args = chunks[1:]

        if command in {"/start", "/help"}:
            self._send(chat_id, HELP_TEXT)
            return

        if command == "/myid":
            self._send(chat_id, f"Ваш chat id: {chat_id}")
            return

        if not self._is_admin_chat(chat_id):
            self._send(chat_id, "Доступ запрещен. Этот чат не имеет прав администратора.")
            return

        if command == "/stats":
            text = (
                "Сводка:\n"
                f"Пользователи: {User.objects.count()}\n"
                f"Новые заявки: {OrderRequest.objects.filter(status='new').count()}\n"
                f"Новые предзаказы: {ShopPreorder.objects.filter(status='new').count()}\n"
                f"Заявки в обработке: {OrderRequest.objects.filter(status='in_progress').count()}\n"
                f"Предзаказы в обработке: {ShopPreorder.objects.filter(status='in_progress').count()}"
            )
            self._send(chat_id, text)
            return

        if command == "/orders":
            limit = self._parse_limit(args)
            rows = OrderRequest.objects.select_related("article").order_by("-created_at")[:limit]
            if not rows:
                self._send(chat_id, "Заявок пока нет.")
                return
            payload = ["Последние заявки:"]
            for row in rows:
                payload.append(
                    f"#{row.id} | {row.get_status_display()} | {row.name} | {row.phone} | {row.created_at:%d.%m %H:%M}"
                )
            self._send(chat_id, "\n".join(payload))
            return

        if command == "/order":
            order_id = self._parse_id_arg(args)
            if order_id is None:
                self._send(chat_id, "Использование: /order <id>")
                return
            order = OrderRequest.objects.filter(pk=order_id).select_related("article", "user").first()
            if not order:
                self._send(chat_id, f"Заявка #{order_id} не найдена.")
                return
            self._send(
                chat_id,
                (
                    f"Заявка #{order.id}\n"
                    f"Статус: {order.get_status_display()} ({order.status})\n"
                    f"Имя: {order.name}\n"
                    f"Телефон: {order.phone}\n"
                    f"Email: {order.email or '-'}\n"
                    f"Способ связи: {order.get_contact_method_display()}\n"
                    f"Статья: {order.article.title if order.article else '-'}\n"
                    f"Пользователь: {order.user.email if order.user else '-'}\n"
                    f"Комментарий: {order.message or '-'}"
                ),
            )
            return

        if command == "/set_order":
            if len(args) < 2:
                self._send(chat_id, "Использование: /set_order <id> <new|in_progress|done>")
                return
            order_id = self._parse_int(args[0])
            new_status = args[1].strip().lower()
            if order_id is None or new_status not in ORDER_STATUS_KEYS:
                self._send(chat_id, "Некорректные параметры. Допустимо: new, in_progress, done.")
                return
            order = OrderRequest.objects.filter(pk=order_id).first()
            if not order:
                self._send(chat_id, f"Заявка #{order_id} не найдена.")
                return
            order.status = new_status
            order.save(update_fields=["status", "updated_at"])
            self._send(chat_id, f"Заявка #{order_id} обновлена: {new_status}")
            return

        if command == "/preorders":
            limit = self._parse_limit(args)
            rows = ShopPreorder.objects.select_related("category", "product", "user").order_by("-created_at")[:limit]
            if not rows:
                self._send(chat_id, "Предзаказов пока нет.")
                return
            payload = ["Последние предзаказы:"]
            for row in rows:
                label = row.product.name if row.product else (row.desired_item or "-")
                payload.append(
                    f"#{row.id} | {row.get_status_display()} | {label} x{row.quantity} | {row.phone} | {row.created_at:%d.%m %H:%M}"
                )
            self._send(chat_id, "\n".join(payload))
            return

        if command == "/preorder":
            preorder_id = self._parse_id_arg(args)
            if preorder_id is None:
                self._send(chat_id, "Использование: /preorder <id>")
                return
            preorder = ShopPreorder.objects.filter(pk=preorder_id).select_related("user", "category", "product").first()
            if not preorder:
                self._send(chat_id, f"Предзаказ #{preorder_id} не найден.")
                return
            self._send(
                chat_id,
                (
                    f"Предзаказ #{preorder.id}\n"
                    f"Статус: {preorder.get_status_display()} ({preorder.status})\n"
                    f"Категория: {preorder.category.name if preorder.category else '-'}\n"
                    f"Товар: {preorder.product.name if preorder.product else (preorder.desired_item or '-')}\n"
                    f"Количество: {preorder.quantity}\n"
                    f"Телефон: {preorder.phone}\n"
                    f"Email: {preorder.email or '-'}\n"
                    f"Пользователь: {preorder.user.email if preorder.user else '-'}\n"
                    f"Комментарий: {preorder.comment or '-'}"
                ),
            )
            return

        if command == "/set_preorder":
            if len(args) < 2:
                self._send(chat_id, "Использование: /set_preorder <id> <new|in_progress|done>")
                return
            preorder_id = self._parse_int(args[0])
            new_status = args[1].strip().lower()
            if preorder_id is None or new_status not in PREORDER_STATUS_KEYS:
                self._send(chat_id, "Некорректные параметры. Допустимо: new, in_progress, done.")
                return
            preorder = ShopPreorder.objects.filter(pk=preorder_id).first()
            if not preorder:
                self._send(chat_id, f"Предзаказ #{preorder_id} не найден.")
                return
            preorder.status = new_status
            preorder.save(update_fields=["status", "updated_at"])
            self._send(chat_id, f"Предзаказ #{preorder_id} обновлен: {new_status}")
            return

        if command == "/admins":
            rows = AdminEmailAccess.objects.filter(is_active=True).order_by("email")
            payload = [f"OWNER_EMAIL: {normalize_email(settings.OWNER_EMAIL) or '-'}", "Активные админы:"]
            payload.extend([f"- {row.email}" for row in rows])
            self._send(chat_id, "\n".join(payload))
            return

        if command == "/grant":
            email = self._parse_email_arg(args)
            if not email:
                self._send(chat_id, "Использование: /grant <email>")
                return
            access, _ = AdminEmailAccess.objects.update_or_create(
                email=email,
                defaults={
                    "is_active": True,
                    "note": f"Granted via Telegram chat {chat_id}",
                },
            )
            self._send(chat_id, f"Админ-доступ включен: {access.email}")
            return

        if command == "/revoke":
            email = self._parse_email_arg(args)
            if not email:
                self._send(chat_id, "Использование: /revoke <email>")
                return
            owner_email = normalize_email(settings.OWNER_EMAIL)
            if email == owner_email:
                self._send(chat_id, "Нельзя отключить owner email.")
                return
            access = AdminEmailAccess.objects.filter(email=email).first()
            if not access:
                self._send(chat_id, f"Админ {email} не найден.")
                return
            access.is_active = False
            access.save(update_fields=["is_active", "updated_at"])
            self._send(chat_id, f"Админ-доступ отключен: {email}")
            return

        self._send(chat_id, "Неизвестная команда. /help")

    def _parse_limit(self, args: list[str]) -> int:
        default = 10
        if not args:
            return default
        value = self._parse_int(args[0])
        if value is None:
            return default
        return max(1, min(value, 50))

    def _parse_id_arg(self, args: list[str]) -> int | None:
        if not args:
            return None
        return self._parse_int(args[0])

    def _parse_int(self, value: str) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _parse_email_arg(self, args: list[str]) -> str:
        if not args:
            return ""
        email = normalize_email(args[0])
        if "@" not in email:
            return ""
        return email
