import logging
from telegram import Update
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    ConversationHandler, CommandHandler, filters
)
from database.queries import (
    get_user, get_cart_items, get_cart_total, create_order,
    add_order_items, clear_cart, update_order_status, update_order_payment,
    get_user_orders, get_order, get_order_items, update_active_shopper
)
from keyboards.checkout import checkout_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.messages import Messages
from utils.formatters import format_price
from utils.payment import zarinpal
from utils.validators import validate_phone, validate_address

logger = logging.getLogger(__name__)

CHECKOUT_ADDRESS, CHECKOUT_PHONE = range(2)


async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start checkout process."""
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id
    await update_active_shopper(telegram_id, "checkout")

    user = await get_user(telegram_id)
    cart_items = await get_cart_items(telegram_id)

    if not cart_items:
        await query.edit_message_text("سبد خرید شما خالی است.")
        return

    total = sum(item["price"] * item["quantity"] for item in cart_items)
    context.user_data["checkout_total"] = total
    context.user_data["checkout_items"] = cart_items

    items_list = "\n".join([f"• {item['name']} x{item['quantity']}" for item in cart_items])
    text = Messages.CHECKOUT_SUMMARY.format(
        items=items_list,
        total=format_price(total),
        address=user['address'] or 'ثبت نشده',
        phone=user['phone'] or 'ثبت نشده'
    )

    await query.edit_message_text(
        text,
        reply_markup=checkout_keyboard()
    )


async def handle_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle checkout inline callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    telegram_id = query.from_user.id
    user = await get_user(telegram_id)

    if data == "change_address":
        await query.edit_message_text(Messages.CHECKOUT_NEW_ADDRESS)
        context.user_data["checkout_step"] = "address"
        return CHECKOUT_ADDRESS

    elif data == "change_phone":
        await query.edit_message_text(Messages.CHECKOUT_NEW_PHONE)
        context.user_data["checkout_step"] = "phone"
        return CHECKOUT_PHONE

    elif data == "cancel_order":
        await query.edit_message_text("سفارش لغو شد.")
        context.user_data.pop("checkout_total", None)
        context.user_data.pop("checkout_items", None)

    elif data == "pay":
        # Create order
        total = context.user_data.get("checkout_total", 0)
        cart_items = context.user_data.get("checkout_items", [])

        if not cart_items:
            await query.edit_message_text("خطا: سبد خرید خالی است.")
            return

        order_id = await create_order(
            telegram_id, total, user["address"], user["phone"]
        )

        # Add order items
        order_items = []
        for item in cart_items:
            order_items.append({
                "product_id": item["product_id"],
                "product_name": item["name"],
                "price": item["price"],
                "quantity": item["quantity"]
            })
        await add_order_items(order_id, order_items)

        # Create ZarinPal payment
        from utils.formatters import to_rial_amount
        rial_amount = to_rial_amount(total)

        result = await zarinpal.create_payment(
            amount=rial_amount,
            description=f"سفارش شماره {order_id}",
            mobile=user["phone"]
        )

        if result["success"]:
            # Store order info for verification
            context.user_data["pending_payment"] = {
                "order_id": order_id,
                "amount": rial_amount,
                "authority": result["authority"]
            }

            await query.edit_message_text(
                f"💳 {Messages.PAYMENT_REDIRECT}\n\n"
                f"شماره سفارش: #{order_id}\n"
                f"مبلغ: {format_price(total)}\n\n"
                f"لینک پرداخت:\n{result['gateway_url']}"
            )
        else:
            await query.edit_message_text(
                f"❌ {result['error']}\n\n"
                f"لطفاً دوباره تلاش کنید."
            )


async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive new address during checkout."""
    address = update.message.text.strip()

    if not validate_address(address):
        await update.message.reply_text(
            "آدرس بسیار کوتاه است. لطفاً آدرس کامل‌تری وارد کنید:"
        )
        return CHECKOUT_ADDRESS

    from database.queries import update_user
    await update_user(update.effective_user.id, address=address)
    context.user_data["checkout_step"] = None

    # Refresh checkout view
    telegram_id = update.effective_user.id
    user = await get_user(telegram_id)
    cart_items = context.user_data.get("checkout_items", [])
    total = context.user_data.get("checkout_total", 0)

    items_list = "\n".join([f"• {item['name']} x{item['quantity']}" for item in cart_items])
    text = Messages.CHECKOUT_SUMMARY.format(
        items=items_list,
        total=format_price(total),
        address=address,
        phone=user['phone'] or 'ثبت نشده'
    )

    await update.message.reply_text(
        "آدرس بروزرسانی شد! ✅\n\n" + text,
        reply_markup=checkout_keyboard()
    )
    return ConversationHandler.END


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive new phone during checkout."""
    phone = update.message.text.strip()

    if not validate_phone(phone):
        await update.message.reply_text(
            "شماره تلفن نامعتبر است. لطفاً دوباره وارد کنید:\n"
            "(مثال: 09123456789)"
        )
        return CHECKOUT_PHONE

    from database.queries import update_user
    await update_user(update.effective_user.id, phone=phone)
    context.user_data["checkout_step"] = None

    # Refresh checkout view
    telegram_id = update.effective_user.id
    user = await get_user(telegram_id)
    cart_items = context.user_data.get("checkout_items", [])
    total = context.user_data.get("checkout_total", 0)

    items_list = "\n".join([f"• {item['name']} x{item['quantity']}" for item in cart_items])
    text = Messages.CHECKOUT_SUMMARY.format(
        items=items_list,
        total=format_price(total),
        address=user['address'] or 'ثبت نشده',
        phone=phone
    )

    await update.message.reply_text(
        "تلفن بروزرسانی شد! ✅\n\n" + text,
        reply_markup=checkout_keyboard()
    )
    return ConversationHandler.END


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's orders."""
    telegram_id = update.effective_user.id
    await update_active_shopper(telegram_id, "orders")

    orders = await get_user_orders(telegram_id)

    if not orders:
        await update.message.reply_text(
            Messages.ORDERS_EMPTY,
            reply_markup=main_menu_keyboard()
        )
        return

    text = f"{Messages.ORDERS_TITLE}\n\n"
    for order in orders[:10]:
        status = Messages.ORDER_STATUS_MAP.get(order["status"], order["status"])
        text += f"📦 #{order['id']} | {status}\n"
        text += f"💰 {format_price(order['total_amount'])}\n"
        text += f"📅 {order['created_at']}\n\n"

    await update.message.reply_text(
        text,
        reply_markup=main_menu_keyboard()
    )


def get_checkout_handler():
    """Get checkout conversation handler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_checkout, pattern=r"^checkout$")
        ],
        states={
            CHECKOUT_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)
            ],
            CHECKOUT_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)
            ],
        },
        fallbacks=[CommandHandler("start", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )


def register_checkout_handlers(app):
    """Register checkout handlers."""
    app.add_handler(CallbackQueryHandler(handle_checkout_callback, pattern=r"^pay$|^change_address$|^change_phone$|^cancel_order$"))
