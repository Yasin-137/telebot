"""Persian message templates for the bot."""


class Messages:
    # ─── General ────────────────────────────────────────────────
    WELCOME = "به فروشگاه خوش آمدید! 🛍\n\nلطفاً از منوی زیر استفاده کنید:"
    MAIN_MENU = "منوی اصلی"
    BACK = "بازگشت"
    CANCEL = "لغو"
    CONFIRM = "تایید"
    ERROR = "خطایی رخ داد. لطفاً دوباره تلاش کنید."
    INVALID_INPUT = "ورودی نامعتبر است. لطفاً دوباره تلاش کنید."

    # ─── Registration ───────────────────────────────────────────
    REG_PHONE = "لطفاً شماره تلفن خود را وارد کنید:"
    REG_ADDRESS = "لطفاً آدرس خود را وارد کنید:"
    REG_SUCCESS = "ثبت نام شما با موفقیت انجام شد! ✅"
    REG_SKIP = "رد شدن"

    # ─── Main Menu ──────────────────────────────────────────────
    MENU_CATALOG = "🛒 فروشگاه"
    MENU_CART = "🛒 سبد خرید"
    MENU_ORDERS = "📦 سفارشات من"
    MENU_PROFILE = "👤 پروفایل"
    MENU_SEARCH = "🔍 جستجو"

    # ─── Catalog ────────────────────────────────────────────────
    CATALOG_TITLE = "دسته‌بندی محصولات"
    PRODUCT_NOT_FOUND = "محصول یافت نشد."
    NO_PRODUCTS = "محصولی در این دسته وجود ندارد."
    ADD_TO_CART = "افزودن به سبد"
    PRODUCT_PRICE = "قیمت: {price}"
    PRODUCT_STOCK = "موجودی: {stock}"
    PRODUCT_ADDED = "محصول به سبد اضافه شد! ✅"

    # ─── Search ─────────────────────────────────────────────────
    SEARCH_PROMPT = "عبارت جستجو را وارد کنید:"
    SEARCH_RESULTS = "نتایج جستجو برای: {query}"
    SEARCH_NO_RESULTS = "نتیجه‌ای یافت نشد."

    # ─── Cart ────────────────────────────────────────────────────
    CART_TITLE = "🛒 سبد خرید شما"
    CART_EMPTY = "سبد خرید شما خالی است."
    CART_TOTAL = "جمع کل: {total}"
    CART_ITEM = "{name}\nقیمت: {price}\nتعداد: {quantity}"
    CART_REMOVE = "حذف"
    CART_INCREASE = "+"
    CART_DECREASE = "-"
    CART_CHECKOUT = "تکمیل خرید"
    CART_CLEARED = "سبد خرید پاک شد."
    QUANTITY_UPDATED = "تعداد بروزرسانی شد."

    # ─── Checkout ────────────────────────────────────────────────
    CHECKOUT_TITLE = "تکمیل خرید"
    CHECKOUT_ADDRESS = "آدرس ارسال: {address}\n\nآیا می‌خواهید آدرس را تغییر دهید?"
    CHECKOUT_NEW_ADDRESS = "آدرس جدید را وارد کنید:"
    CHECKOUT_PHONE = "شماره تلفن: {phone}\n\nآیا می‌خواهید شماره را تغییر دهید?"
    CHECKOUT_NEW_PHONE = "شماره تلفن جدید را وارد کنید:"
    CHECKOUT_SUMMARY = "📋 خلاصه سفارش\n\n{items}\n\n💰 جمع کل: {total}\n\n📍 آدرس: {address}\n📞 تلفن: {phone}"
    CHECKOUT_PAY = "پرداخت"
    CHECKOUT_CANCEL_ORDER = "لغو سفارش"

    # ─── Payment ────────────────────────────────────────────────
    PAYMENT_REDIRECT = "در حال انتقال به درگاه پرداخت..."
    PAYMENT_SUCCESS = "پرداخت با موفقیت انجام شد! ✅\nشماره سفارش: #{order_id}"
    PAYMENT_FAILED = "پرداخت ناموفق بود. ❌"
    PAYMENT_CANCELLED = "پرداخت لغو شد."
    PAYMENT_VERIFY_FAILED = "خطا در تایید پرداخت."

    # ─── Orders ─────────────────────────────────────────────────
    ORDERS_TITLE = "📦 سفارشات شما"
    ORDERS_EMPTY = "شما هنوز سفارشی ثبت نکرده‌اید."
    ORDER_DETAIL = "📦 سفارش #{order_id}\n\n状态: {status}\nتاریخ: {date}\nمبلغ: {amount}\n\n{items}"
    ORDER_STATUS_MAP = {
        "pending": "⏳ در انتظار پرداخت",
        "paid": "✅ پرداخت شده",
        "shipped": "🚚 ارسال شده",
        "delivered": "📦 تحویل شده",
        "cancelled": "❌ لغو شده"
    }

    # ─── Profile ────────────────────────────────────────────────
    PROFILE_TITLE = "👤 پروفایل شما"
    PROFILE_INFO = "نام: {name}\nنام کاربری: @{username}\nتلفن: {phone}\nآدرس: {address}"
    PROFILE_EDIT = "ویرایش پروفایل"
    PROFILE_EDIT_PHONE = "شماره تلفن جدید را وارد کنید:"
    PROFILE_EDIT_ADDRESS = "آدرس جدید را وارد کنید:"
    PROFILE_UPDATED = "پروفایل بروزرسانی شد! ✅"

    # ─── Admin ──────────────────────────────────────────────────
    ADMIN_MENU = "🔧 پنل مدیریت"
    ADMIN_STATS = "📊 آمار فروش"
    ADMIN_ORDERS = "📦 مدیریت سفارشات"
    ADMIN_PRODUCTS = "📝 مدیریت محصولات"
    ADMIN_BROADCAST = "📢 ارسال پیام همگانی"
    ADMIN_USERS = "👥 کاربران فعال"
    ADMIN_ADD_PRODUCT = "➕ افزودن محصول"
    ADMIN_EDIT_PRODUCT = "✏️ ویرایش محصول"
    ADMIN_DELETE_PRODUCT = "🗑 حذف محصول"

    # ─── Admin Stats ────────────────────────────────────────────
    STATS_TEMPLATE = """📊 آمار فروش

📦 کل سفارشات: {total_orders}
💰 درآمد کل: {total_revenue}
👥 تعداد کاربران: {total_users}

⏳ سفارشات در انتظار: {pending_orders}
✅ سفارشات پرداخت شده: {paid_orders}
🚚 سفارشات ارسال شده: {shipped_orders}"""

    # ─── Admin Orders ───────────────────────────────────────────
    ADMIN_ORDERS_TITLE = "مدیریت سفارشات"
    ADMIN_ORDER_ITEM = "📦 #{order_id} | {status}\n👤 {user}\n💰 {amount}"
    ADMIN_ORDER_DETAIL = """📦 سفارش #{order_id}

👤 کاربر: {user}
📍 آدرس: {address}
📞 تلفن: {phone}
💰 مبلغ: {amount}
📋 وضعیت: {status}
📅 تاریخ: {date}

🛒 اقلام:
{items}"""

    # ─── Admin Products ─────────────────────────────────────────
    ADMIN_PRODUCT_NAME = "نام محصول را وارد کنید:"
    ADMIN_PRODUCT_DESC = "توضیحات محصول را وارد کنید:"
    ADMIN_PRODUCT_PRICE = "قیمت محصول (به تومان) را وارد کنید:"
    ADMIN_PRODUCT_IMAGE = "لینک تصویر محصول را وارد کنید (یا رد شدن):"
    ADMIN_PRODUCT_STOCK = "موجودی محصول را وارد کنید:"
    ADMIN_PRODUCT_CATEGORY = "دسته‌بندی محصول را انتخاب کنید:"
    ADMIN_PRODUCT_CREATED = "محصول با موفقیت اضافه شد! ✅"
    ADMIN_PRODUCT_UPDATED = "محصول بروزرسانی شد! ✅"
    ADMIN_PRODUCT_DELETED = "محصول حذف شد! ✅"
    ADMIN_NEW_CATEGORY = "نام دسته‌بندی جدید:"
    ADMIN_CATEGORY_CREATED = "دسته‌بندی اضافه شد! ✅"

    # ─── Admin Broadcast ────────────────────────────────────────
    BROADCAST_PROMPT = "پیام خود را ارسال کنید:"
    BROADCAST_CONFIRM = "آیا می‌خواهید این پیام را به {count} کاربر ارسال کنید?"
    BROADCAST_SENT = "پیام به {count} کاربر ارسال شد! ✅"
    BROADCAST_CANCELLED = "ارسال لغو شد."

    # ─── Admin Active Users ─────────────────────────────────────
    ACTIVE_USERS_TITLE = "👥 کاربران فعال (۳۰ دقیقه اخیر)"
    ACTIVE_USER = "👤 {name} | @{username}\n📱 صفحه: {page}"
    ACTIVE_USERS_EMPTY = "کاربر فعالی یافت نشد."
