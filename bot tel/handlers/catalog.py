import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.queries import (
    get_active_categories, get_products_by_category, get_product,
    search_products as db_search_products, update_active_shopper
)
from keyboards.catalog import (
    category_keyboard, products_keyboard, product_detail_keyboard,
    search_results_keyboard
)
from keyboards.main_menu import main_menu_keyboard, back_keyboard
from utils.messages import Messages
from utils.formatters import format_price

logger = logging.getLogger(__name__)

# Store products in user_data for pagination
_user_products = {}


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product categories."""
    telegram_id = update.effective_user.id
    await update_active_shopper(telegram_id, "categories")

    categories = await get_active_categories()

    if not categories:
        await update.message.reply_text(
            "هنوز دسته‌بندی‌ای وجود ندارد.",
            reply_markup=main_menu_keyboard()
        )
        return

    await update.message.reply_text(
        Messages.CATALOG_TITLE,
        reply_markup=category_keyboard(categories)
    )


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("cat:"):
        category_id = int(data.split(":")[1])
        telegram_id = query.from_user.id
        await update_active_shopper(telegram_id, f"category:{category_id}")

        products = await get_products_by_category(category_id)
        _user_products[telegram_id] = list(products)

        if not products:
            await query.edit_message_text(Messages.NO_PRODUCTS)
            return

        await query.edit_message_text(
            "محصولات دسته‌بندی:",
            reply_markup=products_keyboard(products)
        )

    elif data == "back_to_categories":
        categories = await get_active_categories()
        await query.edit_message_text(
            Messages.CATALOG_TITLE,
            reply_markup=category_keyboard(categories)
        )


async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product pagination."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("page:"):
        page = int(data.split(":")[1])
        telegram_id = query.from_user.id
        products = _user_products.get(telegram_id, [])

        if products:
            await query.edit_message_reply_markup(
                reply_markup=products_keyboard(products, page)
            )


async def handle_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product selection."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("prod:"):
        product_id = int(data.split(":")[1])
        telegram_id = query.from_user.id
        await update_active_shopper(telegram_id, f"product:{product_id}")

        product = await get_product(product_id)
        if not product:
            await query.edit_message_text(Messages.PRODUCT_NOT_FOUND)
            return

        text = (
            f"📦 {product['name']}\n\n"
            f"📝 {product['description'] or 'بدون توضیحات'}\n\n"
            f"💰 {format_price(product['price'])}\n"
            f"📦 موجودی: {product['stock']} عدد\n"
            f"📂 دسته: {product['category_name'] or 'نامشخص'}"
        )

        if product["image_url"]:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=product["image_url"],
                caption=text,
                reply_markup=product_detail_keyboard(product_id)
            )
        else:
            await query.edit_message_text(
                text,
                reply_markup=product_detail_keyboard(product_id)
            )


async def add_to_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add to cart button."""
    query = update.callback_query

    data = query.data
    if data.startswith("addcart:"):
        product_id = int(data.split(":")[1])
        telegram_id = query.from_user.id

        from database.queries import add_to_cart
        await add_to_cart(telegram_id, product_id)

        await query.answer("محصول به سبد اضافه شد! ✅", show_alert=True)


async def handle_back_to_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to products button."""
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id
    products = _user_products.get(telegram_id, [])

    if products:
        await query.edit_message_text(
            "محصولات:",
            reply_markup=products_keyboard(products)
        )
    else:
        categories = await get_active_categories()
        await query.edit_message_text(
            Messages.CATALOG_TITLE,
            reply_markup=category_keyboard(categories)
        )


async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search query."""
    query_text = update.message.text
    telegram_id = update.effective_user.id

    if query_text == "بازگشت":
        context.user_data["awaiting_search"] = False
        await update.message.reply_text(
            Messages.WELCOME,
            reply_markup=main_menu_keyboard()
        )
        return

    await update_active_shopper(telegram_id, f"search:{query_text}")

    products = await db_search_products(query_text)

    if not products:
        await update.message.reply_text(
            Messages.SEARCH_NO_RESULTS,
            reply_markup=main_menu_keyboard()
        )
        return

    _user_products[telegram_id] = list(products)

    await update.message.reply_text(
        f"{Messages.SEARCH_RESULTS.format(query=query_text)}\n\n"
        f"تعداد نتایج: {len(products)}",
        reply_markup=search_results_keyboard(products)
    )


# Register handlers
def register_catalog_handlers(app):
    """Register catalog handlers."""
    app.add_handler(CallbackQueryHandler(handle_category, pattern=r"^cat:|^back_to_categories$"))
    app.add_handler(CallbackQueryHandler(handle_pagination, pattern=r"^page:"))
    app.add_handler(CallbackQueryHandler(handle_product, pattern=r"^prod:"))
    app.add_handler(CallbackQueryHandler(add_to_cart_callback, pattern=r"^addcart:"))
    app.add_handler(CallbackQueryHandler(handle_back_to_products, pattern=r"^back_to_products$"))
