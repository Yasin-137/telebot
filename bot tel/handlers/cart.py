import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.queries import (
    get_cart_items, update_cart_quantity, remove_from_cart,
    clear_cart, get_cart_total, update_active_shopper
)
from keyboards.cart import cart_keyboard, confirm_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.messages import Messages
from utils.formatters import format_price

logger = logging.getLogger(__name__)


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show shopping cart."""
    telegram_id = update.effective_user.id
    await update_active_shopper(telegram_id, "cart")

    cart_items = await get_cart_items(telegram_id)

    if not cart_items:
        await update.message.reply_text(
            Messages.CART_EMPTY,
            reply_markup=main_menu_keyboard()
        )
        return

    text = f"{Messages.CART_TITLE}\n\n"
    total = 0
    for item in cart_items:
        item_total = item["price"] * item["quantity"]
        total += item_total
        text += f"• {item['name']}\n"
        text += f"  قیمت: {format_price(item['price'])}\n"
        text += f"  تعداد: {item['quantity']}\n"
        text += f"  جزئی: {format_price(item_total)}\n\n"

    text += f"💰 {Messages.CART_TOTAL.format(total=format_price(total))}"

    await update.message.reply_text(
        text,
        reply_markup=cart_keyboard(cart_items, telegram_id)
    )


async def handle_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cart inline callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    telegram_id = query.from_user.id

    if data.startswith("cartinc:"):
        product_id = int(data.split(":")[1])
        items = await get_cart_items(telegram_id)
        current_qty = 0
        for item in items:
            if item["product_id"] == product_id:
                current_qty = item["quantity"]
                break

        await update_cart_quantity(telegram_id, product_id, current_qty + 1)
        await _refresh_cart(query, telegram_id)

    elif data.startswith("cartdec:"):
        product_id = int(data.split(":")[1])
        items = await get_cart_items(telegram_id)
        current_qty = 0
        for item in items:
            if item["product_id"] == product_id:
                current_qty = item["quantity"]
                break

        if current_qty > 1:
            await update_cart_quantity(telegram_id, product_id, current_qty - 1)
        else:
            await remove_from_cart(telegram_id, product_id)
        await _refresh_cart(query, telegram_id)

    elif data.startswith("cartdel:"):
        product_id = int(data.split(":")[1])
        await remove_from_cart(telegram_id, product_id)
        await _refresh_cart(query, telegram_id)

    elif data == "cart_clear":
        await query.edit_message_text(
            "آیا مطمئن هستید که می‌خواهید سبد را خالی کنید؟",
            reply_markup=confirm_keyboard()
        )
        context.user_data["pending_action"] = "clear_cart"

    elif data == "confirm_yes":
        pending = context.user_data.get("pending_action")
        if pending == "clear_cart":
            await clear_cart(telegram_id)
            await query.edit_message_text(Messages.CART_CLEARED)
        context.user_data["pending_action"] = None

    elif data == "confirm_no":
        await query.edit_message_text("عملیات لغو شد.")
        context.user_data["pending_action"] = None

    elif data == "cart_total":
        total = await get_cart_total(telegram_id)
        await query.answer(f"جمع کل: {format_price(total)}", show_alert=True)


async def _refresh_cart(query, telegram_id):
    """Refresh cart display after modification."""
    cart_items = await get_cart_items(telegram_id)

    if not cart_items:
        await query.edit_message_text(Messages.CART_EMPTY)
        return

    text = f"{Messages.CART_TITLE}\n\n"
    total = 0
    for item in cart_items:
        item_total = item["price"] * item["quantity"]
        total += item_total
        text += f"• {item['name']}\n"
        text += f"  قیمت: {format_price(item['price'])}\n"
        text += f"  تعداد: {item['quantity']}\n"
        text += f"  جزئی: {format_price(item_total)}\n\n"

    text += f"💰 {Messages.CART_TOTAL.format(total=format_price(total))}"

    await query.edit_message_text(
        text,
        reply_markup=cart_keyboard(cart_items, telegram_id)
    )


def register_cart_handlers(app):
    """Register cart handlers."""
    app.add_handler(CallbackQueryHandler(handle_cart_callback, pattern=r"^cart"))
