"""
Admin Product Management Keyboards

Provides inline keyboards for:
- Product management submenu
- Paginated product list
- Product detail view
- Stock management with +/- buttons
- Category selection
- Delete confirmation
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.formatters import format_price


def products_menu_keyboard():
    """Products management submenu."""
    keyboard = [
        [InlineKeyboardButton("📋 لیست محصولات", callback_data="adm:prodlist")],
        [InlineKeyboardButton("➕ افزودن محصول", callback_data="adm:addprod")],
        [InlineKeyboardButton("✏️ ویرایش محصول", callback_data="adm:editprod")],
        [InlineKeyboardButton("🗑 حذف محصول", callback_data="adm:delprod")],
        [InlineKeyboardButton("🔍 جستجوی محصول", callback_data="adm:prodsearch")],
        [InlineKeyboardButton("➕ افزودن دسته‌بندی", callback_data="adm:addcat")],
        [InlineKeyboardButton("🔙 بازگشت به داشبورد", callback_data="adm:dashboard")],
    ]
    return InlineKeyboardMarkup(keyboard)


def product_list_keyboard(products, page: int, total_pages: int, mode: str = "view"):
    """Paginated product list with navigation.

    Args:
        products: List of product dicts from DB
        page: Current page (0-indexed)
        total_pages: Total number of pages
        mode: 'view', 'edit', or 'delete' - determines callback prefix
    """
    keyboard = []

    for prod in products:
        stock_label = f"موجود: {prod['stock']}" if prod['stock'] > 0 else "ناموجود"
        btn_text = f"[{stock_label}] {prod['name']} - {format_price(prod['price'])}"

        if mode == "edit":
            callback = f"adm:eprod:name:{prod['id']}"
        elif mode == "delete":
            callback = f"adm:delprod:{prod['id']}"
        else:
            callback = f"adm:prod:{prod['id']}"

        keyboard.append([InlineKeyboardButton(btn_text, callback_data=callback)])

    # Pagination controls
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton("◀️ قبلی", callback_data=f"adm:prodpage:{page - 1}:{mode}")
        )
    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("بعدی ▶️", callback_data=f"adm:prodpage:{page + 1}:{mode}")
        )
    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت به منو", callback_data="adm:products")
    ])

    return InlineKeyboardMarkup(keyboard)


def product_detail_keyboard(product_id: int):
    """Product detail view with action buttons."""
    keyboard = [
        [InlineKeyboardButton("✏️ ویرایش نام", callback_data=f"adm:eprod:name:{product_id}")],
        [InlineKeyboardButton("✏️ ویرایش قیمت", callback_data=f"adm:eprod:price:{product_id}")],
        [InlineKeyboardButton("✏️ ویرایش توضیحات", callback_data=f"adm:eprod:desc:{product_id}")],
        [InlineKeyboardButton("🖼 تغییر تصویر", callback_data=f"adm:eprod:image:{product_id}")],
        [InlineKeyboardButton("📦 مدیریت موجودی", callback_data=f"adm:stk:{product_id}")],
        [InlineKeyboardButton("🗑 حذف محصول", callback_data=f"adm:delprod:{product_id}")],
        [InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="adm:prodlist")],
    ]
    return InlineKeyboardMarkup(keyboard)


def stock_management_keyboard(product_id: int, current_stock: int):
    """Stock management with +1/-1 quick adjust buttons."""
    keyboard = [
        [
            InlineKeyboardButton("-10", callback_data=f"adm:stkminus:{product_id}"),
            InlineKeyboardButton("-1", callback_data=f"adm:stkminus:{product_id}"),
        ],
        [
            InlineKeyboardButton(f"موجودی: {current_stock}", callback_data="adm:noop"),
        ],
        [
            InlineKeyboardButton("+1", callback_data=f"adm:stkplus:{product_id}"),
            InlineKeyboardButton("+10", callback_data=f"adm:stkplus:{product_id}"),
        ],
        [InlineKeyboardButton("🔙 بازگشت به محصول", callback_data=f"adm:prod:{product_id}")],
        [InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="adm:prodlist")],
    ]
    return InlineKeyboardMarkup(keyboard)


def category_selection_keyboard(categories):
    """Category selection for add product wizard."""
    keyboard = []
    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(cat["name"], callback_data=f"adm:cat:{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ دسته‌بندی جدید", callback_data="adm:newcat")])
    keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="adm:products")])
    return InlineKeyboardMarkup(keyboard)


def confirm_delete_keyboard(product_id: int):
    """Delete confirmation dialog."""
    keyboard = [
        [InlineKeyboardButton("✅ بله، حذف شود", callback_data=f"adm:confirmdel:{product_id}")],
        [InlineKeyboardButton("❌ انصراف", callback_data=f"adm:prod:{product_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)
