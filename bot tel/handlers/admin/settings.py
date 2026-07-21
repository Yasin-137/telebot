"""
Admin Settings - Bot configuration management.

Features:
- View current bot settings
- View admin list
- Basic configuration display
"""

import logging
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from database.queries import get_user, get_all_users
from keyboards.admin_settings import settings_keyboard
from keyboards.admin_dashboard import back_to_dashboard_keyboard
from config import Config

logger = logging.getLogger(__name__)


async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route settings-related callbacks."""
    query = update.callback_query
    data = query.data

    if data == "adm:settings":
        await show_settings(query, context)
    elif data == "adm:settings:admins":
        await show_admin_list(query, context)
    elif data == "adm:settings:users":
        await show_user_stats(query, context)


async def show_settings(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show bot settings overview."""
    text = (
        "⚙️ تنظیمات ربات\n"
        "================\n\n"
        f"آیدی ادمین‌ها: {', '.join(str(x) for x in Config.ADMIN_IDS)}\n"
        f"مسیر دیتابیس: {Config.DATABASE_PATH}\n"
        f"تعداد اقلام در هر صفحه: {Config.ITEMS_PER_PAGE}\n"
        f"زرین‌پال (سندباکس): {'فعال' if Config.ZARINPAL_SANDBOX else 'غیرفعال'}\n"
    )

    await query.edit_message_text(
        text,
        reply_markup=settings_keyboard()
    )


async def show_admin_list(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show list of admin users."""
    lines = ["👤 لیست ادمین‌ها\n"]

    for admin_id in Config.ADMIN_IDS:
        user = await get_user(admin_id)
        if user:
            name = user['full_name'] or 'ندارد'
            username = user['username'] or 'ندارد'
            lines.append(f"  آیدی: {admin_id}\n  نام: {name}\n  نام کاربری: @{username}\n")
        else:
            lines.append(f"  آیدی: {admin_id}\n  (ثبت‌نام نشده در ربات)\n")

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=settings_keyboard()
    )


async def show_user_stats(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    users = await get_all_users()
    total = len(users)

    await query.edit_message_text(
        f"📊 آمار کاربران\n\n"
        f"تعداد کل کاربران ثبت‌نام شده: {total}\n\n"
        f"آیدی ادمین‌ها: {', '.join(str(x) for x in Config.ADMIN_IDS)}",
        reply_markup=settings_keyboard()
    )
