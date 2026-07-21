"""
Admin Broadcast Keyboards

Provides inline keyboards for broadcast confirmation.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def broadcast_confirm_keyboard():
    """Broadcast confirmation dialog."""
    keyboard = [
        [InlineKeyboardButton("✅ ارسال به همه کاربران", callback_data="adm:broadcast:yes")],
        [InlineKeyboardButton("❌ لغو", callback_data="adm:broadcast:no")],
    ]
    return InlineKeyboardMarkup(keyboard)
