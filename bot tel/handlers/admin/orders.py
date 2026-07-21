"""
Admin Order Management - List, filter, and update order status.

Features:
- View all orders with status filter
- Order detail with items
- Quick status update (pending/paid/shipped/delivered/cancelled)
- Recent orders view
"""

import logging
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from database.queries import (
    get_all_orders, get_order, get_order_items, update_order_status
)
from keyboards.admin_orders import (
    orders_menu_keyboard, order_list_keyboard,
    order_detail_keyboard, order_filter_keyboard
)
from keyboards.admin_dashboard import back_to_dashboard_keyboard
from utils.formatters import format_price
from utils.messages import Messages

logger = logging.getLogger(__name__)


async def handle_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route order-related callbacks."""
    query = update.callback_query
    data = query.data

    if data == "adm:orders":
        await show_orders_menu(query, context)
    elif data.startswith("adm:orders:"):
        status = data.split(":")[-1]
        await show_filtered_orders(query, context, status)
    elif data == "adm:recent":
        await show_recent_orders(query, context)
    elif data.startswith("adm:order:"):
        order_id = int(data.split(":")[-1])
        await show_order_detail(query, context, order_id)
    elif data.startswith("adm:status:"):
        parts = data.split(":")
        order_id = int(parts[2])
        new_status = parts[3]
        await change_order_status(query, context, order_id, new_status)


async def show_orders_menu(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show orders management submenu with filter options."""
    await query.edit_message_text(
        "📦 مدیریت سفارشات\n\nگزینه مورد نظر را انتخاب کنید:",
        reply_markup=orders_menu_keyboard()
    )


async def show_filtered_orders(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                               status: str):
    """Show orders filtered by status."""
    if status == "all":
        orders = await get_all_orders()
    else:
        orders = await get_all_orders(status)

    if not orders:
        await query.edit_message_text(
            f"سفارشی یافت نشد{f' با وضعیت: {status}' if status != 'all' else ''}.",
            reply_markup=orders_menu_keyboard()
        )
        return

    status_label = "همه" if status == "all" else Messages.ORDER_STATUS_MAP.get(status, status)
    await query.edit_message_text(
        f"سفارشات ({status_label}) - {len(orders)} مورد\n\nسفارش مورد نظر را انتخاب کنید:",
        reply_markup=order_list_keyboard(orders)
    )


async def show_recent_orders(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show the 10 most recent orders."""
    from database.queries import get_recent_orders
    orders = await get_recent_orders(limit=10)

    if not orders:
        await query.edit_message_text(
            "هنوز سفارشی ثبت نشده.",
            reply_markup=back_to_dashboard_keyboard()
        )
        return

    await query.edit_message_text(
        f"آخرین سفارشات ({len(orders)} مورد)\n\nسفارش مورد نظر را انتخاب کنید:",
        reply_markup=order_list_keyboard(orders)
    )


async def show_order_detail(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                            order_id: int):
    """Show detailed view of a single order with items."""
    order = await get_order(order_id)
    if not order:
        await query.edit_message_text("سفارش یافت نشد.",
                                      reply_markup=orders_menu_keyboard())
        return

    items = await get_order_items(order_id)
    items_text = "\n".join([
        f"  • {item['product_name']} x{item['quantity']} = {format_price(item['price'] * item['quantity'])}"
        for item in items
    ])

    status = Messages.ORDER_STATUS_MAP.get(order["status"], order["status"])

    text = (
        f"📦 سفارش #{order_id}\n"
        f"{'=' * 30}\n\n"
        f"👤 کاربر: {order['full_name']} (@{order['username'] or 'ندارد'})\n"
        f"📞 تلفن: {order['phone']}\n"
        f"📍 آدرس: {order['address']}\n\n"
        f"🛒 اقلام:\n{items_text}\n\n"
        f"💰 جمع کل: {format_price(order['total_amount'])}\n"
        f"📋 وضعیت: {status}\n"
        f"📅 تاریخ: {order['created_at']}"
    )

    await query.edit_message_text(
        text,
        reply_markup=order_detail_keyboard(order_id)
    )


async def change_order_status(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                              order_id: int, new_status: str):
    """Update an order's status."""
    valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        await query.answer("وضعیت نامعتبر است.", show_alert=True)
        return

    await update_order_status(order_id, new_status)
    status_label = Messages.ORDER_STATUS_MAP.get(new_status, new_status)
    await query.answer(f"وضعیت سفارش #{order_id} به {status_label} تغییر کرد.", show_alert=True)

    # Refresh the order detail view
    await show_order_detail(query, context, order_id)
