def format_price(price: int) -> str:
    """Format price in Iranian Tomans with comma separators."""
    return f"{price:,} تومان"


def format_price_short(price: int) -> str:
    """Format price in short form (e.g., 1.5M)."""
    if price >= 1_000_000:
        return f"{price / 1_000_000:.1f}M تومان"
    elif price >= 1_000:
        return f"{price / 1_000:.0f}K تومان"
    return f"{price} تومان"


def to_rial_amount(amount: int) -> int:
    """Convert Tomans to Rials (1 Toman = 10 Rials)."""
    return amount * 10


def from_rial_amount(amount: int) -> int:
    """Convert Rials to Tomans."""
    return amount // 10


def parse_price(price_str: str) -> int:
    """Parse a user-entered price string into an integer (Tomans).

    Handles thousands separators, the 'تومان' suffix/label, extra
    whitespace, and Persian/Arabic-Indic digits.

    Raises:
        ValueError: if the string doesn't contain a valid number.
    """
    if price_str is None:
        raise ValueError("Price string is empty")

    digit_map = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
    }
    normalized = "".join(digit_map.get(ch, ch) for ch in price_str)

    normalized = (
        normalized.replace("تومان", "")
        .replace(",", "")
        .replace("،", "")
        .strip()
    )

    if not normalized.isdigit():
        raise ValueError(f"Invalid price format: {price_str!r}")

    return int(normalized)
