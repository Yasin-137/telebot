import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)
from database.queries import get_user, create_user, update_user, is_admin
from keyboards.main_menu import main_menu_keyboard
from utils.messages import Messages

logger = logging.getLogger(__name__)

REG_PHONE, REG_ADDRESS = range(2)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    telegram_id = user.id

    # Track activity
    db_user = await get_user(telegram_id)

    if not db_user:
        # New user - start registration
        await create_user(telegram_id, user.username, user.full_name)
        context.user_data["registration_step"] = "phone"
        await update.message.reply_text(
            f"سلام {user.full_name}! 👋\n\n"
            f"به فروشگاه خوش آمدید.\n"
            f"برای ثبت نام، لطفاً شماره تلفن خود را وارد کنید:\n"
            f"(مثال: 09123456789)"
        )
        return REG_PHONE

    # Existing user
    await update.message.reply_text(
        f"خوش آمدید {user.full_name}! 👋\n\n{Messages.WELCOME}",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive phone number during registration."""
    phone = update.message.text.strip()

    # Basic validation
    if len(phone) < 10 or not phone.isdigit():
        await update.message.reply_text(
            "شماره تلفن نامعتبر است. لطفاً دوباره وارد کنید:\n"
            "(مثال: 09123456789)"
        )
        return REG_PHONE

    await update_user(update.effective_user.id, phone=phone)
    context.user_data["registration_step"] = "address"

    await update.message.reply_text(
        "شماره تلفن ذخیره شد! ✅\n\n"
        "لطفاً آدرس ارسال خود را وارد کنید:"
    )
    return REG_ADDRESS


async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive address during registration."""
    address = update.message.text.strip()

    if len(address) < 10:
        await update.message.reply_text(
            "آدرس بسیار کوتاه است. لطفاً آدرس کامل‌تری وارد کنید:"
        )
        return REG_ADDRESS

    await update_user(update.effective_user.id, address=address)

    await update.message.reply_text(
        f"{Messages.REG_SUCCESS}\n\n{Messages.WELCOME}",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile."""
    user = await get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("خطایی رخ داد. لطفاً دوباره /start کنید.")
        return

    text = (
        f"👤 پروفایل شما\n\n"
        f"نام: {user['full_name']}\n"
        f"نام کاربری: @{user['username'] or 'ندارد'}\n"
        f"تلفن: {user['phone'] or 'ثبت نشده'}\n"
        f"آدرس: {user['address'] or 'ثبت نشده'}"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button presses."""
    text = update.message.text
    telegram_id = update.effective_user.id

    # ─── Checkout: change address ───
    if context.user_data.get("checkout_step") == "address":
        from handlers.checkout import receive_address as checkout_receive_address
        return await checkout_receive_address(update, context)

    # ─── Checkout: change phone ───
    if context.user_data.get("checkout_step") == "phone":
        from handlers.checkout import receive_phone as checkout_receive_phone
        return await checkout_receive_phone(update, context)

    # ─── Admin: editing product value ───
    if context.user_data.get("editing_product"):
        from handlers.admin.products import receive_edit_value
        return await receive_edit_value(update, context)

    # ─── Admin: adding standalone category ───
    if context.user_data.get("adding_category"):
        from handlers.admin.products import receive_new_category
        return await receive_new_category(update, context)

    # ─── Admin: receiving broadcast message ───
    if context.user_data.get("awaiting_broadcast"):
        from handlers.admin.broadcast import receive_broadcast_message
        return await receive_broadcast_message(update, context)

    # ─── Search mode ───
    if context.user_data.get("awaiting_search"):
        from handlers.catalog import search_products
        return await search_products(update, context)

    # Check for admin
    if await is_admin(telegram_id):
        if text == Messages.ADMIN_MENU or text == "🔧 پنل مدیریت":
            from handlers.admin.dashboard import show_admin_panel
            return await show_admin_panel(update, context)

    if text == Messages.MENU_CATALOG:
        from handlers.catalog import show_categories
        return await show_categories(update, context)
    elif text == Messages.MENU_CART:
        from handlers.cart import show_cart
        return await show_cart(update, context)
    elif text == Messages.MENU_ORDERS:
        from handlers.checkout import show_orders
        return await show_orders(update, context)
    elif text == Messages.MENU_PROFILE:
        return await show_profile(update, context)
    elif text == Messages.MENU_SEARCH:
        context.user_data["awaiting_search"] = True
        await update.message.reply_text(
            Messages.SEARCH_PROMPT,
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("بازگشت")]], resize_keyboard=True)
        )
        return
    elif text == Messages.BACK:
        await update.message.reply_text(
            Messages.WELCOME,
            reply_markup=main_menu_keyboard()
        )


def get_start_handler():
    """Get the start conversation handler."""
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            REG_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)
            ],
            REG_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
    )
