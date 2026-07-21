import os
from dotenv import load_dotenv

# لود کردن فایل .env
load_dotenv(override=True)


class Config:
    # ==================== توکن ربات ====================
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN not found! Add BOT_TOKEN=<your_token> to your .env file."
        )

    # ==================== تنظیمات ادمین ====================
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "7105490811").split(",") if x.strip()]

    # ==================== زرین‌پال ====================
    ZARINPAL_MERCHANT_ID = os.getenv("ZARINPAL_MERCHANT_ID", "")
    ZARINPAL_CALLBACK_URL = os.getenv("ZARINPAL_CALLBACK_URL", "")
    ZARINPAL_SANDBOX = os.getenv("ZARINPAL_SANDBOX", "True").lower() == "true"

    # ==================== دیتابیس ====================
    DATABASE_PATH = os.getenv("DATABASE_PATH", "database/bot.db")

    # ==================== پراکسی ====================
    PROXY_URL = os.getenv("PROXY_URL", "")  # مثال: socks5://user:pass@host:port یا http://host:port

    # ==================== تنظیمات عمومی ====================
    ITEMS_PER_PAGE = 5
    ZARINPAL_API = "https://api.zarinpal.com/pg/v4"
    ZARINPAL_SANDBOX_API = "https://sandbox.zarinpal.com/pg/v4"


# تست (اختیاری)
if __name__ == "__main__":
    print("✅ BOT_TOKEN loaded successfully!")
    print("Token length:", len(Config.BOT_TOKEN))
    print("Starts with:", Config.BOT_TOKEN[:15] + "...")