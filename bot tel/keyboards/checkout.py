from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def checkout_keyboard():
    """Checkout options keyboard."""
    keyboard = [
        [InlineKeyboardButton("💳 پرداخت", callback_data="pay")],
        [InlineKeyboardButton("📝 تغییر آدرس", callback_data="change_address")],
        [InlineKeyboardButton("📞 تغییر تلفن", callback_data="change_phone")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)


def address_keyboard(has_address: bool):
    """Address selection keyboard."""
    keyboard = []
    if has_address:
        keyboard.append([InlineKeyboardButton("✅ استفاده از آدرس فعلی", callback_data="use_current_address")])
    keyboard.append([InlineKeyboardButton("📝 آدرس جدید", callback_data="new_address")])
    keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_order")])
    return InlineKeyboardMarkup(keyboard)


def phone_keyboard(has_phone: bool):
    """Phone selection keyboard."""
    keyboard = []
    if has_phone:
        keyboard.append([InlineKeyboardButton("✅ استفاده از تلفن فعلی", callback_data="use_current_phone")])
    keyboard.append([InlineKeyboardButton("📞 تلفن جدید", callback_data="new_phone")])
    keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_order")])
    return InlineKeyboardMarkup(keyboard)
