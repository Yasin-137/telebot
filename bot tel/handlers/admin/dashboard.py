"""
Admin Dashboard - Enhanced statistics and overview.

Provides a comprehensive dashboard with:
- Total registered users
- Active users in last 7 days
- Successful purchases & total revenue
- Users currently in shopping cart
- Abandoned carts (cart items with no recent order)
- Quick navigation to other admin sections
"""

import logging
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from database.queries import (
    get_dashboard_stats, get_active_shoppers, get_active_categories
)
from keyboards.admin_dashboard import dashboard_keyboard
from utils.formatters import format_price

logger = logging.getLogger(__name__)


async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: /admin command or menu button. Shows the dashboard."""
    telegram_id = update.effective_user.id
    from handlers.admin import is_admin_user

    if not is_admin_user(telegram_id):
        await update.message.reply_text("شما دسترسی مدیریت ندارید.")
        return

    await show_dashboard_message(update, context)


async def show_dashboard_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show dashboard as a new message (for /admin command)."""
    stats = await get_dashboard_stats()
    text = _format_dashboard(stats)

    await update.message.reply_text(
        text,
        reply_markup=dashboard_keyboard()
    )


async def show_dashboard(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show dashboard by editing the current message."""
    stats = await get_dashboard_stats()
    text = _format_dashboard(stats)

    await query.edit_message_text(
        text,
        reply_markup=dashboard_keyboard()
    )


async def show_active_users(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show users currently active (last 30 minutes)."""
    shoppers = await get_active_shoppers(30)

    if not shoppers:
        await query.edit_message_text(
            "کاربر فعالی در ۳۰ دقیقه اخیر یافت نشد.",
            reply_markup=dashboard_keyboard()
        )
        return

    lines = ["👥 کاربران فعال (۳۰ دقیقه اخیر)\n"]
    for i, shopper in enumerate(shoppers[:20], 1):
        name = shopper['full_name'] or 'ندارد'
        username = shopper['username'] or 'ندارد'
        page = shopper['current_page'] or 'نامشخص'
        activity = shopper['last_activity'] or 'نامشخص'
        lines.append(
            f"{i}. {name} (@{username})\n"
            f"   صفحه: {page}\n"
            f"   آخرین فعالیت: {activity}"
        )

    if len(shoppers) > 20:
        lines.append(f"\n... و {len(shoppers) - 20} کاربر دیگر")

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=dashboard_keyboard()
    )


def _format_dashboard(stats: dict) -> str:
    """Format dashboard statistics into a readable message."""
    return (
        "🔧 پنل مدیریت\n"
        "================\n\n"
        f"👥 کاربران\n"
        f"   کل ثبت‌نام شده:     {stats['total_users']}\n"
        f"   فعال (۷ روز اخیر):   {stats['active_users_7d']}\n\n"
        f"📦 سفارشات و درآمد\n"
        f"   کل سفارشات:         {stats['total_orders']}\n"
        f"   خریدهای موفق:        {stats['successful_purchases']}\n"
        f"   در انتظار:           {stats['pending_orders']}\n"
        f"   درآمد کل:            {format_price(stats['total_revenue'])}\n\n"
        f"🛒 سبد خرید\n"
        f"   کاربران با سبد:      {stats['users_in_cart']}\n"
        f"   سبد رها شده:         {stats['abandoned_carts']}\n\n"
        f"📝 فروشگاه\n"
        f"   محصولات:             {stats['total_products']}\n"
        f"   دسته‌بندی‌ها:         {stats['total_categories']}\n"
        "\n"
        "بخش مورد نظر را انتخاب کنید:"
    )
