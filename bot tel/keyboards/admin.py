from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.messages import Messages


def admin_main_keyboard():
    """Admin main panel inline keyboard."""
    keyboard = [
        [InlineKeyboardButton(Messages.ADMIN_STATS, callback_data="adm:stats")],
        [InlineKeyboardButton(Messages.ADMIN_ORDERS, callback_data="adm:orders")],
        [InlineKeyboardButton(Messages.ADMIN_PRODUCTS, callback_data="adm:products")],
        [InlineKeyboardButton(Messages.ADMIN_BROADCAST, callback_data="adm:broadcast")],
        [InlineKeyboardButton(Messages.ADMIN_USERS, callback_data="adm:users")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_orders_keyboard():
    """Admin orders filter keyboard."""
    keyboard = [
        [InlineKeyboardButton("همه سفارشات", callback_data="adm:orders:all")],
        [InlineKeyboardButton("⏳ در انتظار", callback_data="adm:orders:pending")],
        [InlineKeyboardButton("✅ پرداخت شده", callback_data="adm:orders:paid")],
        [InlineKeyboardButton("🚚 ارسال شده", callback_data="adm:orders:shipped")],
        [InlineKeyboardButton("📦 تحویل شده", callback_data="adm:orders:delivered")],
        [InlineKeyboardButton("❌ لغو شده", callback_data="adm:orders:cancelled")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm:back")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_order_detail_keyboard(order_id: int):
    """Admin single order detail keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("⏳ در انتظار", callback_data=f"adm:status:{order_id}:pending"),
            InlineKeyboardButton("✅ پرداخت شده", callback_data=f"adm:status:{order_id}:paid"),
        ],
        [
            InlineKeyboardButton("🚚 ارسال شده", callback_data=f"adm:status:{order_id}:shipped"),
            InlineKeyboardButton("📦 تحویل شده", callback_data=f"adm:status:{order_id}:delivered"),
        ],
        [InlineKeyboardButton("❌ لغو شده", callback_data=f"adm:status:{order_id}:cancelled")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm:orders")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_products_keyboard():
    """Admin products management keyboard."""
    keyboard = [
        [InlineKeyboardButton(Messages.ADMIN_ADD_PRODUCT, callback_data="adm:addprod")],
        [InlineKeyboardButton(Messages.ADMIN_EDIT_PRODUCT, callback_data="adm:editprod")],
        [InlineKeyboardButton(Messages.ADMIN_DELETE_PRODUCT, callback_data="adm:delprod")],
        [InlineKeyboardButton("➕ افزودن دسته‌بندی", callback_data="adm:addcat")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm:back")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_product_list_keyboard(products):
    """Admin product list for edit/delete."""
    keyboard = []
    for prod in products:
        keyboard.append([
            InlineKeyboardButton(
                f"{prod['name']}",
                callback_data=f"adm:prod:{prod['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="adm:products")])
    return InlineKeyboardMarkup(keyboard)


def admin_product_actions_keyboard(product_id: int):
    """Admin single product actions."""
    keyboard = [
        [InlineKeyboardButton("✏️ ویرایش نام", callback_data=f"adm:eprod:name:{product_id}")],
        [InlineKeyboardButton("✏️ ویرایش قیمت", callback_data=f"adm:eprod:price:{product_id}")],
        [InlineKeyboardButton("✏️ ویرایش توضیحات", callback_data=f"adm:eprod:desc:{product_id}")],
        [InlineKeyboardButton("✏️ ویرایش موجودی", callback_data=f"adm:eprod:stock:{product_id}")],
        [InlineKeyboardButton("🖼 تغییر تصویر", callback_data=f"adm:eprod:image:{product_id}")],
        [InlineKeyboardButton("🗑 حذف محصول", callback_data=f"adm:delprod:{product_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm:products")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_category_keyboard(categories):
    """Admin category selection keyboard."""
    keyboard = []
    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(cat["name"], callback_data=f"adm:cat:{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ دسته‌بندی جدید", callback_data="adm:newcat")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="adm:products")])
    return InlineKeyboardMarkup(keyboard)


def admin_broadcast_confirm_keyboard():
    """Admin broadcast confirmation."""
    keyboard = [
        [InlineKeyboardButton("✅ ارسال", callback_data="adm:broadcast:yes")],
        [InlineKeyboardButton("❌ لغو", callback_data="adm:broadcast:no")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_order_list_keyboard(orders):
    """Admin order list keyboard."""
    keyboard = []
    for order in orders[:10]:  # Show last 10 orders
        status_emoji = {
            "pending": "⏳", "paid": "✅",
            "shipped": "🚚", "delivered": "📦", "cancelled": "❌"
        }.get(order["status"], "❓")
        keyboard.append([
            InlineKeyboardButton(
                f"{status_emoji} #{order['id']} - {order['total_amount']:,} تومان",
                callback_data=f"adm:order:{order['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="adm:back")])
    return InlineKeyboardMarkup(keyboard)
