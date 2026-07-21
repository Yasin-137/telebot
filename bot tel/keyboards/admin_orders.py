"""
Admin Order Management Keyboards

Provides inline keyboards for:
- Orders management submenu
- Order list with status indicators
- Order detail with status change buttons
- Status filter options
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def orders_menu_keyboard():
    """Orders management submenu."""
    keyboard = [
        [InlineKeyboardButton("همه سفارشات", callback_data="adm:orders:all")],
        [InlineKeyboardButton("📦 آخرین سفارشات", callback_data="adm:recent")],
        [InlineKeyboardButton("--- فیلتر بر اساس وضعیت ---", callback_data="adm:noop")],
        [InlineKeyboardButton("⏳ در انتظار", callback_data="adm:orders:pending")],
        [InlineKeyboardButton("✅ پرداخت شده", callback_data="adm:orders:paid")],
        [InlineKeyboardButton("🚚 ارسال شده", callback_data="adm:orders:shipped")],
        [InlineKeyboardButton("📦 تحویل شده", callback_data="adm:orders:delivered")],
        [InlineKeyboardButton("❌ لغو شده", callback_data="adm:orders:cancelled")],
        [InlineKeyboardButton("🔙 بازگشت به داشبورد", callback_data="adm:dashboard")],
    ]
    return InlineKeyboardMarkup(keyboard)


def order_list_keyboard(orders):
    """Order list with status emoji indicators."""
    keyboard = []

    for order in orders[:10]:  # Max 10 orders per page
        status_emoji = {
            "pending": "⏳", "paid": "✅",
            "shipped": "🚚", "delivered": "📦", "cancelled": "❌"
        }.get(order["status"], "❓")

        user_name = order.get('full_name', 'ندارد')
        if len(user_name) > 20:
            user_name = user_name[:18] + ".."

        btn_text = f"{status_emoji} #{order['id']} | {user_name} | {order['total_amount']:,} تومان"
        keyboard.append([
            InlineKeyboardButton(btn_text, callback_data=f"adm:order:{order['id']}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت به سفارشات", callback_data="adm:orders")
    ])

    return InlineKeyboardMarkup(keyboard)


def order_detail_keyboard(order_id: int):
    """Order detail with status change buttons."""
    keyboard = [
        [
            InlineKeyboardButton("⏳ در انتظار", callback_data=f"adm:status:{order_id}:pending"),
            InlineKeyboardButton("✅ پرداخت شده", callback_data=f"adm:status:{order_id}:paid"),
        ],
        [
            InlineKeyboardButton("🚚 ارسال شده", callback_data=f"adm:status:{order_id}:shipped"),
            InlineKeyboardButton("📦 تحویل شده", callback_data=f"adm:status:{order_id}:delivered"),
        ],
        [InlineKeyboardButton("❌ لغو سفارش", callback_data=f"adm:status:{order_id}:cancelled")],
        [InlineKeyboardButton("🔙 بازگشت به سفارشات", callback_data="adm:orders")],
    ]
    return InlineKeyboardMarkup(keyboard)


def order_filter_keyboard():
    """Status filter options."""
    keyboard = [
        [InlineKeyboardButton("همه سفارشات", callback_data="adm:orders:all")],
        [InlineKeyboardButton("⏳ در انتظار", callback_data="adm:orders:pending")],
        [InlineKeyboardButton("✅ پرداخت شده", callback_data="adm:orders:paid")],
        [InlineKeyboardButton("🚚 ارسال شده", callback_data="adm:orders:shipped")],
        [InlineKeyboardButton("📦 تحویل شده", callback_data="adm:orders:delivered")],
        [InlineKeyboardButton("❌ لغو شده", callback_data="adm:orders:cancelled")],
        [InlineKeyboardButton("🔙 بازگشت به داشبورد", callback_data="adm:dashboard")],
    ]
    return InlineKeyboardMarkup(keyboard)
