"""
Admin Dashboard Inline Keyboard

Provides the main navigation keyboard for the admin panel.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def dashboard_keyboard():
    """Main admin dashboard navigation keyboard."""
    keyboard = [
        [InlineKeyboardButton("📝 مدیریت محصولات", callback_data="adm:products")],
        [InlineKeyboardButton("📦 مدیریت سفارشات", callback_data="adm:orders")],
        [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="adm:broadcast")],
        [InlineKeyboardButton("👥 کاربران فعال", callback_data="adm:users")],
        [InlineKeyboardButton("⚙️ تنظیمات ربات", callback_data="adm:settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_dashboard_keyboard():
    """Back to dashboard button."""
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت به داشبورد", callback_data="adm:dashboard")]
    ]
    return InlineKeyboardMarkup(keyboard)
