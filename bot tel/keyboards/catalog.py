from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
from utils.formatters import format_price


def category_keyboard(categories):
    """Inline keyboard for categories."""
    keyboard = []
    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(cat["name"], callback_data=f"cat:{cat['id']}")
        ])
    return InlineKeyboardMarkup(keyboard)


def products_keyboard(products, page: int = 0):
    """Inline keyboard for products with pagination."""
    keyboard = []
    start = page * Config.ITEMS_PER_PAGE
    end = start + Config.ITEMS_PER_PAGE
    page_products = products[start:end]

    for prod in page_products:
        text = f"{prod['name']} - {format_price(prod['price'])}"
        keyboard.append([
            InlineKeyboardButton(text, callback_data=f"prod:{prod['id']}")
        ])

    # Pagination buttons
    pagination = []
    if page > 0:
        pagination.append(InlineKeyboardButton("◀️ قبلی", callback_data=f"page:{page-1}"))
    if end < len(products):
        pagination.append(InlineKeyboardButton("▶️ بعدی", callback_data=f"page:{page+1}"))
    if pagination:
        keyboard.append(pagination)

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت به دسته‌ها", callback_data="back_to_categories")
    ])

    return InlineKeyboardMarkup(keyboard)


def product_detail_keyboard(product_id: int):
    """Inline keyboard for product detail view."""
    keyboard = [
        [
            InlineKeyboardButton("🛒 افزودن به سبد", callback_data=f"addcart:{product_id}")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_products")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def search_results_keyboard(products):
    """Inline keyboard for search results."""
    keyboard = []
    for prod in products:
        text = f"{prod['name']} - {format_price(prod['price'])}"
        keyboard.append([
            InlineKeyboardButton(text, callback_data=f"prod:{prod['id']}")
        ])
    return InlineKeyboardMarkup(keyboard)
