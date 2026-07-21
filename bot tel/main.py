import logging
import signal
import sys
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.request import HTTPXRequest
from telegram.error import NetworkError, TimedOut
import config
import database.models
import database
from handlers.start import get_start_handler, handle_menu
from handlers.catalog import register_catalog_handlers
from handlers.cart import register_cart_handlers
from handlers.checkout import (
    get_checkout_handler, register_checkout_handlers, show_orders
)
from handlers.admin import (
    show_admin_panel, register_admin_handlers
)
from keyboards.main_menu import main_menu_keyboard

# Configure logging - suppress noisy httpx logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def post_init(application: Application):
    """Initialize database after bot starts."""
    await database.models.init_db()
    logger.info("Database initialized.")


async def post_shutdown(application: Application):
    """Cleanup on shutdown."""
    await database.close_db()
    logger.info("Database closed.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors - only log real errors, not expected network retries."""
    if isinstance(context.error, (NetworkError, TimedOut)):
        # Network errors are expected with unstable proxy - just retry silently
        pass
    else:
        logger.error(f"Unhandled exception: {context.error}", exc_info=context.error)


def main():
    """Start the bot with auto-restart on crash."""
    while True:
        try:
            _run_bot()
            break  # Normal exit
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Bot crashed: {e}. Restarting in 5 seconds...")
            import time
            time.sleep(5)


def _run_bot():
    """Run the bot single cycle."""
    # Custom request with shorter timeouts and proxy for unstable connection
    request = HTTPXRequest(
        connect_timeout=10,
        read_timeout=15,
        write_timeout=15,
        pool_timeout=5,
        proxy=config.Config.PROXY_URL or None,
    )

    builder = (
        Application.builder()
        .token(config.Config.BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .request(request)
    )

    if config.Config.PROXY_URL:
        logger.info(f"Proxy: {config.Config.PROXY_URL[:25]}...")

    application = builder.build()

    # Error handler - silently retry on network errors
    application.add_error_handler(error_handler)

    # Conversation handlers (order matters - more specific first)
    application.add_handler(get_start_handler())
    application.add_handler(get_checkout_handler())

    # Register modular admin handlers
    register_admin_handlers(application)

    # Register callback query handlers for non-admin modules
    register_catalog_handlers(application)
    register_cart_handlers(application)
    register_checkout_handlers(application)

    # Command handlers
    application.add_handler(CommandHandler("orders", show_orders))

    # Handle main menu text buttons (catch-all, must be last)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)
    )

    # Start polling
    logger.info("Bot starting...")
    application.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
        poll_interval=1.0,
        bootstrap_retries=10,
    )


if __name__ == "__main__":
    main()
