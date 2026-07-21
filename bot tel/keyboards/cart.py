from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.formatters import format_price


def cart_keyboard(cart_items, user_id: int):
    """Inline keyboard for cart items."""
    keyboard = []
    for item in cart_items:
        # Product name
        keyboard.append([
            InlineKeyboardButton(
                f"{item['name']} ({item['quantity']}x)",
                callback_data=f"cartview:{item['product_id']}"
            )
        ])
        # Quantity controls
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"cartdec:{item['product_id']}"),
            InlineKeyboardButton(f"{item['quantity']}", callback_data=f"cartqty:{item['product_id']}"),
            InlineKeyboardButton("➕", callback_data=f"cartinc:{item['product_id']}"),
            InlineKeyboardButton("🗑", callback_data=f"cartdel:{item['product_id']}"),
        ])

    if cart_items:
        total = sum(item["price"] * item["quantity"] for item in cart_items)
        keyboard.append([
            InlineKeyboardButton(
                f"💰 جمع کل: {format_price(total)}",
                callback_data="cart_total"
            )
        ])
        keyboard.append([
            InlineKeyboardButton("✅ تکمیل خرید", callback_data="checkout")
        ])
        keyboard.append([
            InlineKeyboardButton("🗑 خالی کردن سبد", callback_data="cart_clear")
        ])

    return InlineKeyboardMarkup(keyboard)


def confirm_keyboard():
    """Confirmation inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("✅ بله", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ خیر", callback_data="confirm_no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

