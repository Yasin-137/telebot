from telegram import ReplyKeyboardMarkup, KeyboardButton
from utils.messages import Messages


def main_menu_keyboard():
    """Main menu keyboard."""
    keyboard = [
        [KeyboardButton(Messages.MENU_CATALOG)],
        [KeyboardButton(Messages.MENU_CART), KeyboardButton(Messages.MENU_ORDERS)],
        [KeyboardButton(Messages.MENU_PROFILE), KeyboardButton(Messages.MENU_SEARCH)],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def admin_menu_keyboard():
    """Admin menu keyboard."""
    keyboard = [
        [KeyboardButton(Messages.ADMIN_STATS), KeyboardButton(Messages.ADMIN_ORDERS)],
        [KeyboardButton(Messages.ADMIN_PRODUCTS), KeyboardButton(Messages.ADMIN_BROADCAST)],
        [KeyboardButton(Messages.ADMIN_USERS)],
        [KeyboardButton(Messages.BACK)],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_keyboard():
    """Simple back button."""
    keyboard = [[KeyboardButton(Messages.BACK)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
