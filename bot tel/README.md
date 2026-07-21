# 🛍 Telegram E-Commerce Shopping Bot

A production-ready Telegram e-commerce bot built with Python, featuring a complete shopping cart system, ZarinPal payment integration, and comprehensive admin panel.

## Features

### Customer Features
- **Product Catalog** - Browse categories, view products with images and descriptions
- **Shopping Cart** - Add, remove, adjust quantities, view total
- **Search** - Search products by name or description
- **Checkout** - Seamless checkout with address and phone management
- **Payment** - Secure payment via ZarinPal (Iranian gateway)
- **Order History** - View past orders and their status

### Admin Features
- **Dashboard** - Real-time sales statistics
- **Order Management** - View and update order statuses (pending, paid, shipped, delivered)
- **Product Management** - Add, edit, delete products with categories
- **Broadcast** - Send announcements to all users
- **Active Users** - Monitor real-time active shoppers

### Technical Features
- **Persian/Farsi Interface** - Full RTL support
- **SQLite Database** - Persistent storage with WAL mode
- **Async Architecture** - Built with python-telegram-bot v20+
- **Modular Code** - Clean separation of concerns
- **Error Handling** - Graceful error handling throughout
- **Logging** - Comprehensive logging for debugging

## Project Structure

```
bot tel/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── database/
│   ├── __init__.py            # Database connection
│   ├── models.py              # Table creation
│   └── queries.py             # Database operations
│
├── handlers/
│   ├── __init__.py
│   ├── start.py               # Registration flow
│   ├── catalog.py             # Product browsing
│   ├── cart.py                # Cart management
│   ├── checkout.py            # Checkout & payment
│   └── admin.py               # Admin panel
│
├── keyboards/
│   ├── __init__.py
│   ├── main_menu.py           # Reply keyboards
│   ├── catalog.py             # Catalog inline keyboards
│   ├── cart.py                # Cart inline keyboards
│   ├── checkout.py            # Checkout keyboards
│   └── admin.py               # Admin keyboards
│
└── utils/
    ├── __init__.py
    ├── payment.py              # ZarinPal integration
    ├── messages.py             # Persian text templates
    ├── formatters.py           # Price formatting
    └── validators.py           # Input validation
```

## Installation

### 1. Clone or Download

```bash
git clone <repository-url>
cd "bot tel"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
copy .env.example .env
```

Edit `.env`:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_telegram_id,another_admin_id
ZARINPAL_MERCHANT_ID=your_zarinpal_merchant_id
ZARINPAL_CALLBACK_URL=https://yourdomain.com/verify
ZARINPAL_SANDBOX=True
DATABASE_PATH=database/bot.db
```

### 5. Get Bot Token

1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow the prompts
3. Copy the token to your `.env` file

### 6. Get Admin Telegram ID

1. Open Telegram and search for @userinfobot
2. Send any message to get your Telegram ID
3. Add it to `ADMIN_IDS` in `.env`

### 7. Setup ZarinPal

1. Register at [ZarinPal](https://zarinpal.com)
2. Get your merchant ID from the dashboard
3. For testing, use sandbox mode (`ZARINPAL_SANDBOX=True`)

## Usage

### Start the Bot

```bash
python main.py
```

### Customer Commands

- `/start` - Start the bot and register
- Browse catalog using menu buttons
- Add products to cart
- Complete checkout and pay

### Admin Commands

- `/admin` - Access admin panel
- View statistics, manage orders, products, and broadcast messages

## Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `users` | User profiles with Telegram info |
| `categories` | Product categories |
| `products` | Product catalog |
| `cart_items` | Shopping cart items |
| `orders` | Customer orders |
| `order_items` | Order line items |
| `active_shoppers` | Real-time activity tracking |

## Payment Flow

1. Customer adds products to cart
2. Proceeds to checkout
3. Confirms address and phone
4. Clicks "Pay" button
5. Bot creates ZarinPal payment request
6. Customer is redirected to ZarinPal gateway
7. After payment, ZarinPal redirects to callback URL
8. Bot verifies payment and updates order status

## Deployment

### Polling Mode (Development)

The bot runs in polling mode by default. This is suitable for development and small-scale deployments.

### Webhook Mode (Production)

For production, consider switching to webhook mode:

1. Set up HTTPS endpoint
2. Update `main.py` to use webhook
3. Configure `ZARINPAL_CALLBACK_URL`

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | Required |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | Required |
| `ZARINPAL_MERCHANT_ID` | ZarinPal merchant ID | Required |
| `ZARINPAL_CALLBACK_URL` | Payment callback URL | Required |
| `ZARINPAL_SANDBOX` | Use ZarinPal sandbox | `True` |
| `DATABASE_PATH` | SQLite database path | `database/bot.db` |

## Security Notes

- Never commit `.env` file
- Keep your bot token secret
- Use sandbox mode for testing
- Validate all user inputs
- Implement rate limiting for production

## Troubleshooting

### Bot doesn't start
- Check `BOT_TOKEN` in `.env`
- Ensure all dependencies are installed
- Check Python version (3.10+)

### Payment fails
- Verify ZarinPal merchant ID
- Check callback URL is accessible
- Ensure sandbox mode is enabled for testing

### Database errors
- Check write permissions in project directory
- Delete `bot.db` to reset database

## License

This project is open source and available for personal and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on GitHub

---

**Note:** This bot is designed for Iranian e-commerce with Persian/Farsi interface and Iranian Rial currency.
