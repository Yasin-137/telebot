"""
Admin Settings Keyboards

Provides inline keyboards for bot settings management.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def settings_keyboard():
    """Settings menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("👤 لیست ادمین‌ها", callback_data="adm:settings:admins")],
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="adm:settings:users")],
        [InlineKeyboardButton("🔙 بازگشت به داشبورد", callback_data="adm:dashboard")],
    ]
    return InlineKeyboardMarkup(keyboard)
