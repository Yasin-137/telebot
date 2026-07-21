import re


def validate_phone(phone: str) -> bool:
    """Validate Iranian phone number."""
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, phone))


def validate_price(price_str: str) -> bool:
    """Validate price input."""
    try:
        price = int(price_str.replace(",", "").replace("،", ""))
        return price > 0
    except (ValueError, AttributeError):
        return False


def parse_price(price_str: str) -> int:
    """Parse price string to integer."""
    cleaned = price_str.replace(",", "").replace("،", "").strip()
    return int(cleaned)


def validate_address(address: str) -> bool:
    """Validate address is not empty and has minimum length."""
    return bool(address and len(address.strip()) >= 10)
