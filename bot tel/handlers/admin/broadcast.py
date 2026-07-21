"""
Admin Broadcast Messaging - Send messages to all users.

Features:
- Compose broadcast message
- Preview before sending
- Confirm and send with progress tracking
- Send to all registered users with error handling
"""

import logging
from telegram import Update, CallbackQuery
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler,
    CallbackQueryHandler, CommandHandler, filters
)

from database.queries import get_all_users
from keyboards.admin_broadcast import broadcast_confirm_keyboard
from keyboards.admin_dashboard import back_to_dashboard_keyboard

logger = logging.getLogger(__name__)

BROADCAST_MESSAGE = 0


async def handle_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route broadcast-related callbacks."""
    query = update.callback_query
    data = query.data

    if data == "adm:broadcast":
        await start_broadcast(query, context)
    elif data == "adm:broadcast:yes":
        await send_broadcast(query, context)
    elif data == "adm:broadcast:no":
        await query.edit_message_text(
            "ارسال لغو شد.",
            reply_markup=back_to_dashboard_keyboard()
        )
        context.user_data.pop("broadcast_message", None)


async def start_broadcast(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast composition."""
    await query.edit_message_text(
        "پیام خود را برای ارسال به همه کاربران وارد کنید:"
    )
    context.user_data["awaiting_broadcast"] = True


async def receive_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive broadcast message text and show confirmation."""
    if not context.user_data.get("awaiting_broadcast"):
        return ConversationHandler.END

    message = update.message.text
    context.user_data["broadcast_message"] = message
    context.user_data["awaiting_broadcast"] = False

    users = await get_all_users()
    preview = (
        f"پیش‌نمایش پیام\n"
        f"{'=' * 30}\n\n"
        f"{message}\n\n"
        f"{'=' * 30}\n"
        f"تعداد دریافت‌کنندگان: {len(users)} کاربر\n\n"
        f"آیا می‌خواهید این پیام را ارسال کنید?"
    )

    await update.message.reply_text(
        preview,
        reply_markup=broadcast_confirm_keyboard()
    )
    return ConversationHandler.END


async def send_broadcast(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Execute broadcast to all users."""
    message = context.user_data.get("broadcast_message")
    if not message:
        await query.edit_message_text(
            "خطا: پیامی یافت نشد.",
            reply_markup=back_to_dashboard_keyboard()
        )
        return

    users = await get_all_users()
    sent = 0
    failed = 0

    for user in users:
        try:
            await query.bot.send_message(
                chat_id=user["telegram_id"],
                text=f"📢 پیام مدیریت:\n\n{message}"
            )
            sent += 1
        except Exception as e:
            logger.error(f"خطا در ارسال پیام به {user['telegram_id']}: {e}")
            failed += 1

    context.user_data.pop("broadcast_message", None)

    result = (
        f"ارسال پیام همگانی تکمیل شد\n"
        f"{'=' * 30}\n\n"
        f"ارسال شده: {sent}\n"
        f"ناموفق: {failed}\n"
        f"کل کاربران: {len(users)}"
    )

    await query.edit_message_text(
        result,
        reply_markup=back_to_dashboard_keyboard()
    )


def get_admin_broadcast_handler():
    """Get the broadcast conversation handler for registration."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_broadcast, pattern=r"^adm:broadcast$")
        ],
        states={
            BROADCAST_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_broadcast_message)
            ],
        },
        fallbacks=[CommandHandler("start", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )
