"""
Admin Panel - Modular Handler Package

This package provides a complete admin panel with:
- Dashboard with enhanced statistics
- Product management (CRUD + quick stock)
- Order management with status tracking
- Broadcast messaging
- Bot settings

All admin access is restricted to user IDs listed in Config.ADMIN_IDS.
"""

from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler
)

from .dashboard import show_admin_panel, show_dashboard
from .products import (
    get_admin_product_handler,
    show_products_menu, handle_product_callback,
    receive_new_category, receive_edit_value
)
from .orders import (
    handle_orders_callback, show_recent_orders
)
from .broadcast import (
    get_admin_broadcast_handler,
    receive_broadcast_message
)
from .settings import handle_settings_callback


def is_admin_user(telegram_id: int) -> bool:
    """Check if a user is an authorized admin."""
    from config import Config
    return telegram_id in Config.ADMIN_IDS


def register_admin_handlers(app: Application):
    """Register ALL admin handlers with the application.

    Conversation handlers are registered first (higher priority),
    then callback query handlers, then the /admin command.
    """
    # Conversation handlers (must be registered first for priority)
    app.add_handler(get_admin_product_handler())
    app.add_handler(get_admin_broadcast_handler())

    # Admin callback router (handles all adm:* callbacks)
    app.add_handler(CallbackQueryHandler(
        _route_admin_callback,
        pattern=r"^adm:"
    ))

    # /admin command
    app.add_handler(CommandHandler("admin", show_admin_panel))


async def _route_admin_callback(update, context):
    """Central router for all admin callback queries.

    Routes to the appropriate handler based on callback data prefix.
    Note: query.answer() is called by individual handlers to allow
    custom alert messages (e.g., stock adjustments).
    """
    query = update.callback_query
    data = query.data
    telegram_id = query.from_user.id

    if not is_admin_user(telegram_id):
        await query.answer("شما دسترسی مدیریت ندارید.", show_alert=True)
        return

    # Noop callback (for display-only buttons)
    if data == "adm:noop":
        await query.answer()
        return

    # Stock adjustment callbacks get their own answer (with alert)
    if data.startswith(("adm:stkplus:", "adm:stkminus:")):
        await handle_product_callback(update, context)
        return

    # Order status change gets its own answer (with alert)
    if data.startswith("adm:status:"):
        await handle_orders_callback(update, context)
        return

    # Delete confirmation gets its own answer (with alert)
    if data.startswith("adm:confirmdel:"):
        await handle_product_callback(update, context)
        return

    # Default: answer silently then route
    await query.answer()

    # Dashboard
    if data in ("adm:dashboard", "adm:stats", "adm:back"):
        await show_dashboard(query, context)

    # Products
    elif data in ("adm:products", "adm:prodlist", "adm:addprod",
                  "adm:editprod", "adm:delprod", "adm:addcat") or \
         data.startswith(("adm:prod:", "adm:eprod:", "adm:delprod:",
                          "adm:cat:", "adm:newcat", "adm:stk:",
                          "adm:prodpage:", "adm:prodsearch")):
        await handle_product_callback(update, context)

    # Orders
    elif data in ("adm:orders", "adm:orders:all", "adm:recent") or \
         data.startswith("adm:order:"):
        await handle_orders_callback(update, context)

    # Broadcast (conversation handler takes priority, but just in case)
    elif data in ("adm:broadcast", "adm:broadcast:yes", "adm:broadcast:no"):
        from .broadcast import handle_broadcast_callback
        await handle_broadcast_callback(update, context)

    # Settings
    elif data.startswith("adm:settings"):
        await handle_settings_callback(update, context)

    # Active users (legacy compat)
    elif data == "adm:users":
        from .dashboard import show_active_users
        await show_active_users(query, context)
