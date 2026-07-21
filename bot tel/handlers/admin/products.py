"""
Admin Product Management - Complete CRUD with search and quick stock.

Features:
- Add product (multi-step wizard)
- Edit product fields (name, description, price, stock, image)
- Delete product (with confirmation)
- Product list with search/filter
- Quick stock management (+/- buttons)
- Category management
"""

import logging
from telegram import Update, CallbackQuery
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    ConversationHandler, CommandHandler, filters
)

from database.queries import (
    get_product, get_all_products_admin, create_product, update_product,
    delete_product, get_active_categories, create_category,
    get_product_stock, update_product_stock
)
from keyboards.admin_products import (
    products_menu_keyboard, product_list_keyboard,
    product_detail_keyboard,
    category_selection_keyboard, stock_management_keyboard,
    confirm_delete_keyboard
)
from keyboards.admin_dashboard import back_to_dashboard_keyboard
from utils.formatters import format_price
from utils.validators import validate_price
from utils.formatters import parse_price as fmt_parse_price

logger = logging.getLogger(__name__)

# Conversation states for add product wizard
ADD_NAME, ADD_DESC, ADD_PRICE, ADD_IMAGE, ADD_STOCK, ADD_CATEGORY = range(6)
EDIT_VALUE = 6

# Product list pagination state
PRODUCTS_PER_PAGE = 8


# ─── Callback Router ───────────────────────────────────────────

async def handle_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route product-related callbacks."""
    query = update.callback_query
    data = query.data

    if data == "adm:products":
        await show_products_menu(query, context)
    elif data == "adm:prodlist":
        context.user_data["prod_page"] = 0
        context.user_data["prod_search"] = None
        await show_product_list(query, context, page=0)
    elif data == "adm:addprod":
        # This is handled by the ConversationHandler entry point
        pass
    elif data == "adm:editprod":
        context.user_data["prod_page"] = 0
        context.user_data["prod_search"] = None
        await show_product_list(query, context, page=0, mode="edit")
    elif data == "adm:delprod":
        context.user_data["prod_page"] = 0
        context.user_data["prod_search"] = None
        await show_product_list(query, context, page=0, mode="delete")
    elif data.startswith("adm:prod:"):
        product_id = int(data.split(":")[-1])
        await show_product_detail(query, context, product_id)
    elif data.startswith("adm:prodpage:"):
        parts = data.split(":")
        page = int(parts[2])
        mode = parts[3] if len(parts) > 3 else "view"
        await show_product_list(query, context, page, mode)
    elif data.startswith("adm:prodsearch"):
        context.user_data["admin_search_mode"] = "product"
        await query.edit_message_text(
            "عبارت جستجو را وارد کنید:",
            reply_markup=back_to_dashboard_keyboard()
        )
    elif data.startswith("adm:eprod:"):
        parts = data.split(":")
        field = parts[2]
        product_id = int(parts[3])
        await start_edit_field(query, context, field, product_id)
    elif data.startswith("adm:stkplus:"):
        product_id = int(data.split(":")[-1])
        await quick_stock_adjust(query, context, product_id, +1)
    elif data.startswith("adm:stkminus:"):
        product_id = int(data.split(":")[-1])
        await quick_stock_adjust(query, context, product_id, -1)
    elif data.startswith("adm:stk:"):
        product_id = int(data.split(":")[-1])
        await show_stock_management(query, context, product_id)
    elif data.startswith("adm:delprod:"):
        product_id = int(data.split(":")[-1])
        await show_delete_confirmation(query, context, product_id)
    elif data.startswith("adm:confirmdel:"):
        product_id = int(data.split(":")[-1])
        await confirm_delete_product(query, context, product_id)
    elif data == "adm:addcat":
        await start_add_category(query, context)
    elif data.startswith("adm:cat:"):
        category_id = int(data.split(":")[-1])
        await handle_category_selection(query, context, category_id)
    elif data == "adm:newcat":
        await prompt_new_category(query, context)


# ─── Products Menu ─────────────────────────────────────────────

async def show_products_menu(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Show the products management submenu."""
    await query.edit_message_text(
        "📝 مدیریت محصولات\n\nعملیات مورد نظر را انتخاب کنید:",
        reply_markup=products_menu_keyboard()
    )


# ─── Product List with Search ──────────────────────────────────

async def show_product_list(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                            page: int = 0, mode: str = "view"):
    """Show paginated product list with optional search filter."""
    search = context.user_data.get("prod_search")
    products = await get_all_products_admin(search)

    if not products:
        text = "محصولی یافت نشد." if not search else f"نتیجه‌ای برای '{search}' یافت نشد."
        await query.edit_message_text(text, reply_markup=products_menu_keyboard())
        return

    # Paginate
    total = len(products)
    total_pages = (total + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
    start = page * PRODUCTS_PER_PAGE
    end = min(start + PRODUCTS_PER_PAGE, total)
    page_products = products[start:end]

    mode_label = {
        "view": "",
        "edit": " - محصول مورد نظر را برای ویرایش انتخاب کنید",
        "delete": " - محصول مورد نظر را برای حذف انتخاب کنید"
    }
    search_label = f"\nجستجو: '{search}'" if search else ""

    header = (
        f"لیست محصولات ({total} مورد){search_label}\n"
        f"صفحه {page + 1}/{total_pages}\n"
        f"{mode_label.get(mode, '')}"
    )

    await query.edit_message_text(
        header,
        reply_markup=product_list_keyboard(page_products, page, total_pages, mode)
    )


# ─── Product Detail ────────────────────────────────────────────

async def show_product_detail(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                              product_id: int):
    """Show detailed view of a single product."""
    product = await get_product(product_id)
    if not product:
        await query.edit_message_text("محصول یافت نشد.",
                                      reply_markup=products_menu_keyboard())
        return

    text = (
        f"📦 {product['name']}\n\n"
        f"📝 توضیحات: {product['description'] or 'ندارد'}\n"
        f"💰 قیمت: {format_price(product['price'])}\n"
        f"📦 موجودی: {product['stock']} عدد\n"
        f"📂 دسته‌بندی: {product['category_name'] or 'نامشخص'}\n"
        f"🖼 تصویر: {'دارد' if product['image_url'] else 'ندارد'}\n"
        f"وضعیت: {'فعال' if product['is_active'] else 'غیرفعال'}"
    )

    await query.edit_message_text(
        text,
        reply_markup=product_detail_keyboard(product_id)
    )


# ─── Quick Stock Management ───────────────────────────────────

async def show_stock_management(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                                product_id: int):
    """Show quick stock adjustment interface with +/- buttons."""
    product = await get_product(product_id)
    if not product:
        await query.edit_message_text("محصول یافت نشد.",
                                      reply_markup=products_menu_keyboard())
        return

    text = (
        f"📦 مدیریت موجودی: {product['name']}\n\n"
        f"موجودی فعلی: {product['stock']} عدد\n"
        f"قیمت: {format_price(product['price'])}\n\n"
        f"از دکمه‌ها برای تغییر موجودی استفاده کنید."
    )

    await query.edit_message_text(
        text,
        reply_markup=stock_management_keyboard(product_id, product['stock'])
    )


async def quick_stock_adjust(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                             product_id: int, delta: int):
    """Adjust stock by +1 or -1."""
    current = await get_product_stock(product_id)
    new_stock = max(0, current + delta)
    await update_product_stock(product_id, new_stock)

    product = await get_product(product_id)
    if not product:
        return

    action = "افزایش" if delta > 0 else "کاهش"
    await query.answer(f"موجودی {action} یافت! جدید: {new_stock}", show_alert=False)

    # Refresh the stock management view
    text = (
        f"📦 مدیریت موجودی: {product['name']}\n\n"
        f"موجودی فعلی: {new_stock} عدد\n"
        f"قیمت: {format_price(product['price'])}\n\n"
        f"موجودی {action} یافت."
    )
    await query.edit_message_text(
        text,
        reply_markup=stock_management_keyboard(product_id, new_stock)
    )


# ─── Edit Product Fields ──────────────────────────────────────

async def start_edit_field(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                           field: str, product_id: int):
    """Start editing a product field (name, price, desc, stock, image)."""
    field_names = {
        "name": "نام", "price": "قیمت", "desc": "توضیحات",
        "stock": "موجودی", "image": "تصویر"
    }
    field_name = field_names.get(field, field)

    # Map short field names to DB column names
    db_field_map = {"desc": "description", "image": "image_url"}
    db_field = db_field_map.get(field, field)

    context.user_data["editing_product"] = {
        "field": db_field,
        "product_id": product_id,
        "original_field": field
    }

    await query.edit_message_text(f"مقدار جدید {field_name} را وارد کنید:")
    return EDIT_VALUE


async def receive_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the new value for an edited product field."""
    if not context.user_data.get("editing_product"):
        return ConversationHandler.END

    edit_info = context.user_data["editing_product"]
    field = edit_info["field"]
    product_id = edit_info["product_id"]
    value = update.message.text

    # Validate field-specific input
    if field == "price":
        if not validate_price(value):
            await update.message.reply_text("قیمت نامعتبر است. لطفاً دوباره وارد کنید:")
            return EDIT_VALUE
        value = fmt_parse_price(value)
    elif field == "stock":
        try:
            value = int(value)
            if value < 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("موجودی نامعتبر است. لطفاً عدد صحیح وارد کنید:")
            return EDIT_VALUE

    await update_product(product_id, **{field: value})
    context.user_data.pop("editing_product", None)

    # Show the updated product
    product = await get_product(product_id)
    if product:
        text = (
            f"محصول بروزرسانی شد!\n\n"
            f"نام: {product['name']}\n"
            f"قیمت: {format_price(product['price'])}\n"
            f"موجودی: {product['stock']}"
        )
        await update.message.reply_text(
            text,
            reply_markup=product_detail_keyboard(product_id)
        )
    else:
        await update.message.reply_text("محصول بروزرسانی شد!")

    return ConversationHandler.END


# ─── Delete Product ────────────────────────────────────────────

async def show_delete_confirmation(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                                   product_id: int):
    """Show delete confirmation for a product."""
    product = await get_product(product_id)
    if not product:
        await query.edit_message_text("محصول یافت نشد.",
                                      reply_markup=products_menu_keyboard())
        return

    text = (
        f"آیا از حذف این محصول اطمینان دارید?\n\n"
        f"نام: {product['name']}\n"
        f"قیمت: {format_price(product['price'])}\n"
        f"موجودی: {product['stock']}\n\n"
        f"این عمل قابل بازگشت نیست."
    )

    await query.edit_message_text(
        text,
        reply_markup=confirm_delete_keyboard(product_id)
    )


async def confirm_delete_product(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                                 product_id: int):
    """Confirm and execute product deletion."""
    await delete_product(product_id)
    await query.answer("محصول حذف شد!", show_alert=True)

    # Return to product list
    context.user_data["prod_page"] = 0
    await show_product_list(query, context, page=0, mode="delete")


# ─── Category Management ──────────────────────────────────────

async def start_add_category(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for new category name."""
    await query.edit_message_text(
        "نام دسته‌بندی جدید را وارد کنید:",
        reply_markup=back_to_dashboard_keyboard()
    )
    context.user_data["adding_category"] = True


async def prompt_new_category(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Handle new category button during product add wizard."""
    await query.edit_message_text("نام دسته‌بندی جدید را وارد کنید:")
    context.user_data["adding_category"] = True


async def handle_category_selection(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE,
                                    category_id: int):
    """Handle category selection during add product wizard."""
    product_data = context.user_data.get("add_product", {})
    if not product_data:
        await query.edit_message_text("جلسه منقضی شده. دوباره شروع کنید.",
                                      reply_markup=products_menu_keyboard())
        return

    await create_product(
        category_id=category_id,
        name=product_data["name"],
        description=product_data["description"],
        price=product_data["price"],
        image_url=product_data.get("image_url"),
        stock=product_data.get("stock", 0)
    )

    context.user_data.pop("add_product", None)
    await query.edit_message_text(
        "محصول با موفقیت اضافه شد!",
        reply_markup=products_menu_keyboard()
    )


async def receive_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive new category name text from admin."""
    if not context.user_data.get("adding_category"):
        return

    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("نام دسته‌بندی خالی است. لطفاً نامی وارد کنید:")
        return

    await create_category(name)
    context.user_data["adding_category"] = False

    await update.message.reply_text(
        f"دسته‌بندی '{name}' اضافه شد!",
        reply_markup=products_menu_keyboard()
    )


# ─── Add Product Wizard (ConversationHandler) ─────────────────

async def start_add_product(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Start the add product wizard."""
    context.user_data["add_product"] = {}
    await query.edit_message_text("نام محصول را وارد کنید:")
    return ADD_NAME


async def receive_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_product"]["name"] = update.message.text
    await update.message.reply_text("توضیحات محصول را وارد کنید:")
    return ADD_DESC


async def receive_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_product"]["description"] = update.message.text
    await update.message.reply_text("قیمت محصول (به تومان) را وارد کنید:")
    return ADD_PRICE


async def receive_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text
    if not validate_price(price_text):
        await update.message.reply_text("قیمت نامعتبر است. لطفاً دوباره وارد کنید:")
        return ADD_PRICE
    context.user_data["add_product"]["price"] = fmt_parse_price(price_text)
    await update.message.reply_text(
        "لینک تصویر محصول را وارد کنید (یا رد شدن):"
    )
    return ADD_IMAGE


async def receive_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text != "رد شدن":
        context.user_data["add_product"]["image_url"] = text
    await update.message.reply_text("موجودی محصول را وارد کنید:")
    return ADD_STOCK


async def receive_product_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stock = int(update.message.text)
        if stock < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("موجودی نامعتبر است. لطفاً عدد صحیح وارد کنید:")
        return ADD_STOCK

    context.user_data["add_product"]["stock"] = stock

    # Show category selection
    categories = await get_active_categories()
    if not categories:
        await update.message.reply_text(
            "هنوز دسته‌بندی‌ای وجود ندارد. ابتدا دسته‌بندی اضافه کنید."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "دسته‌بندی محصول را انتخاب کنید:",
        reply_markup=category_selection_keyboard(categories)
    )
    return ADD_CATEGORY


async def handle_add_product_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection callback during add product wizard."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("adm:cat:"):
        category_id = int(data.split(":")[-1])
        product_data = context.user_data.get("add_product", {})

        await create_product(
            category_id=category_id,
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            image_url=product_data.get("image_url"),
            stock=product_data.get("stock", 0)
        )

        context.user_data.pop("add_product", None)
        await query.edit_message_text(
            "محصول با موفقیت اضافه شد!",
            reply_markup=products_menu_keyboard()
        )
        return ConversationHandler.END

    elif data == "adm:newcat":
        await query.edit_message_text("نام دسته‌بندی جدید را وارد کنید:")
        context.user_data["adding_category"] = True
        return ADD_CATEGORY


def get_admin_product_handler():
    """Get the product conversation handler for registration."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add_product, pattern=r"^adm:addprod$")
        ],
        states={
            ADD_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_name)
            ],
            ADD_DESC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_desc)
            ],
            ADD_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_price)
            ],
            ADD_IMAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_image)
            ],
            ADD_STOCK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_stock)
            ],
            ADD_CATEGORY: [
                CallbackQueryHandler(handle_add_product_category, pattern=r"^adm:cat:|^adm:newcat$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_category)
            ],
            EDIT_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edit_value)
            ],
        },
        fallbacks=[CommandHandler("start", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )
