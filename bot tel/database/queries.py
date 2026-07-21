from datetime import datetime
from database import get_db


# ─── User Queries ──────────────────────────────────────────────

async def get_user(telegram_id: int):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    return await cursor.fetchone()


async def create_user(telegram_id: int, username: str = None, full_name: str = None):
    db = await get_db()
    await db.execute(
        "INSERT OR IGNORE INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
        (telegram_id, username, full_name)
    )
    await db.commit()


async def update_user(telegram_id: int, **kwargs):
    db = await get_db()
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [telegram_id]
    await db.execute(f"UPDATE users SET {fields} WHERE telegram_id = ?", values)
    await db.commit()


async def is_admin(telegram_id: int) -> bool:
    db = await get_db()
    cursor = await db.execute("SELECT is_admin FROM users WHERE telegram_id = ?", (telegram_id,))
    row = await cursor.fetchone()
    return row and row["is_admin"] == 1


async def get_all_users():
    db = await get_db()
    cursor = await db.execute("SELECT telegram_id FROM users")
    return await cursor.fetchall()


# ─── Category Queries ──────────────────────────────────────────

async def get_active_categories():
    db = await get_db()
    cursor = await db.execute("SELECT * FROM categories WHERE is_active = 1")
    return await cursor.fetchall()


async def get_category(category_id: int):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    return await cursor.fetchone()


async def create_category(name: str, description: str = None):
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO categories (name, description) VALUES (?, ?)",
        (name, description)
    )
    await db.commit()
    return cursor.lastrowid


async def update_category(category_id: int, **kwargs):
    db = await get_db()
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [category_id]
    await db.execute(f"UPDATE categories SET {fields} WHERE id = ?", values)
    await db.commit()


async def delete_category(category_id: int):
    db = await get_db()
    await db.execute("UPDATE categories SET is_active = 0 WHERE id = ?", (category_id,))
    await db.commit()


# ─── Product Queries ───────────────────────────────────────────

async def get_products_by_category(category_id: int, active_only: bool = True):
    db = await get_db()
    condition = "AND p.is_active = 1" if active_only else ""
    cursor = await db.execute(
        f"""SELECT p.*, c.name as category_name FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = ? {condition}
            ORDER BY p.created_at DESC""",
        (category_id,)
    )
    return await cursor.fetchall()


async def get_product(product_id: int):
    db = await get_db()
    cursor = await db.execute(
        """SELECT p.*, c.name as category_name FROM products p
           LEFT JOIN categories c ON p.category_id = c.id
           WHERE p.id = ?""",
        (product_id,)
    )
    return await cursor.fetchone()


async def search_products(query: str):
    db = await get_db()
    cursor = await db.execute(
        """SELECT p.*, c.name as category_name FROM products p
           LEFT JOIN categories c ON p.category_id = c.id
           WHERE p.is_active = 1 AND (p.name LIKE ? OR p.description LIKE ?)
           ORDER BY p.created_at DESC""",
        (f"%{query}%", f"%{query}%")
    )
    return await cursor.fetchall()


async def create_product(category_id: int, name: str, description: str,
                         price: int, image_url: str = None, stock: int = 0):
    db = await get_db()
    cursor = await db.execute(
        """INSERT INTO products (category_id, name, description, price, image_url, stock)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (category_id, name, description, price, image_url, stock)
    )
    await db.commit()
    return cursor.lastrowid


async def update_product(product_id: int, **kwargs):
    db = await get_db()
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [product_id]
    await db.execute(f"UPDATE products SET {fields} WHERE id = ?", values)
    await db.commit()


async def delete_product(product_id: int):
    db = await get_db()
    await db.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
    await db.commit()


# ─── Cart Queries ──────────────────────────────────────────────

async def get_cart_items(user_id: int):
    db = await get_db()
    cursor = await db.execute(
        """SELECT ci.*, p.name, p.price, p.image_url, p.stock
           FROM cart_items ci
           JOIN products p ON ci.product_id = p.id
           WHERE ci.user_id = ? AND p.is_active = 1""",
        (user_id,)
    )
    return await cursor.fetchall()


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    db = await get_db()
    existing = await db.execute(
        "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    item = await existing.fetchone()
    if item:
        await db.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?",
            (quantity, user_id, product_id)
        )
    else:
        await db.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user_id, product_id, quantity)
        )
    await db.commit()


async def update_cart_quantity(user_id: int, product_id: int, quantity: int):
    db = await get_db()
    if quantity <= 0:
        await db.execute(
            "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
    else:
        await db.execute(
            "UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
            (quantity, user_id, product_id)
        )
    await db.commit()


async def remove_from_cart(user_id: int, product_id: int):
    db = await get_db()
    await db.execute(
        "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    await db.commit()


async def clear_cart(user_id: int):
    db = await get_db()
    await db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
    await db.commit()


async def get_cart_total(user_id: int) -> int:
    db = await get_db()
    cursor = await db.execute(
        """SELECT COALESCE(SUM(ci.quantity * p.price), 0) as total
           FROM cart_items ci
           JOIN products p ON ci.product_id = p.id
           WHERE ci.user_id = ?""",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row["total"] if row else 0


# ─── Order Queries ─────────────────────────────────────────────

async def create_order(user_id: int, total_amount: int, address: str, phone: str):
    db = await get_db()
    cursor = await db.execute(
        """INSERT INTO orders (user_id, total_amount, address, phone)
           VALUES (?, ?, ?, ?)""",
        (user_id, total_amount, address, phone)
    )
    await db.commit()
    return cursor.lastrowid


async def add_order_items(order_id: int, items: list):
    db = await get_db()
    for item in items:
        await db.execute(
            """INSERT INTO order_items (order_id, product_id, product_name, price, quantity)
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, item["product_id"], item["product_name"],
             item["price"], item["quantity"])
        )
    await db.commit()


async def get_order(order_id: int):
    db = await get_db()
    cursor = await db.execute(
        """SELECT o.*, u.telegram_id, u.username, u.full_name
           FROM orders o
           JOIN users u ON o.user_id = u.id
           WHERE o.id = ?""",
        (order_id,)
    )
    return await cursor.fetchone()


async def get_order_items(order_id: int):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM order_items WHERE order_id = ?",
        (order_id,)
    )
    return await cursor.fetchall()


async def get_user_orders(user_id: int):
    db = await get_db()
    cursor = await db.execute(
        """SELECT * FROM orders WHERE user_id = ?
           ORDER BY created_at DESC""",
        (user_id,)
    )
    return await cursor.fetchall()


async def get_all_orders(status: str = None):
    db = await get_db()
    if status:
        cursor = await db.execute(
            """SELECT o.*, u.telegram_id, u.username, u.full_name
               FROM orders o JOIN users u ON o.user_id = u.id
               WHERE o.status = ? ORDER BY o.created_at DESC""",
            (status,)
        )
    else:
        cursor = await db.execute(
            """SELECT o.*, u.telegram_id, u.username, u.full_name
               FROM orders o JOIN users u ON o.user_id = u.id
               ORDER BY o.created_at DESC"""
        )
    return await cursor.fetchall()


async def update_order_status(order_id: int, status: str):
    db = await get_db()
    await db.execute(
        "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, order_id)
    )
    await db.commit()


async def update_order_payment(order_id: int, payment_ref: str):
    db = await get_db()
    await db.execute(
        "UPDATE orders SET payment_ref = ?, status = 'paid', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (payment_ref, order_id)
    )
    await db.commit()


# ─── Active Shoppers ──────────────────────────────────────────

async def update_active_shopper(user_id: int, current_page: str = None):
    db = await get_db()
    await db.execute(
        """INSERT INTO active_shoppers (user_id, last_activity, current_page)
           VALUES (?, CURRENT_TIMESTAMP, ?)
           ON CONFLICT(user_id) DO UPDATE SET
           last_activity = CURRENT_TIMESTAMP, current_page = ?""",
        (user_id, current_page, current_page)
    )
    await db.commit()


async def get_active_shoppers(minutes: int = 30):
    db = await get_db()
    cursor = await db.execute(
        """SELECT a.*, u.telegram_id, u.username, u.full_name
           FROM active_shoppers a
           JOIN users u ON a.user_id = u.id
           WHERE a.last_activity > datetime('now', ? || ' minutes')
           ORDER BY a.last_activity DESC""",
        (f"-{minutes}",)
    )
    return await cursor.fetchall()


# ─── Statistics ────────────────────────────────────────────────

async def get_sales_stats():
    db = await get_db()
    stats = {}

    cursor = await db.execute("SELECT COUNT(*) as count FROM orders")
    row = await cursor.fetchone()
    stats["total_orders"] = row["count"]

    cursor = await db.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE status = 'paid'"
    )
    row = await cursor.fetchone()
    stats["total_revenue"] = row["total"]

    cursor = await db.execute("SELECT COUNT(*) as count FROM users")
    row = await cursor.fetchone()
    stats["total_users"] = row["count"]

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM orders WHERE status = 'pending'"
    )
    row = await cursor.fetchone()
    stats["pending_orders"] = row["count"]

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM orders WHERE status = 'paid'"
    )
    row = await cursor.fetchone()
    stats["paid_orders"] = row["count"]

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM orders WHERE status = 'shipped'"
    )
    row = await cursor.fetchone()
    stats["shipped_orders"] = row["count"]

    return stats


# ─── Enhanced Dashboard Stats ─────────────────────────────────

async def get_dashboard_stats():
    """Get comprehensive dashboard statistics."""
    db = await get_db()
    stats = {}

    # Total registered users
    cursor = await db.execute("SELECT COUNT(*) as count FROM users")
    row = await cursor.fetchone()
    stats["total_users"] = row["count"]

    # Active users in last 7 days (based on last activity or order creation)
    cursor = await db.execute(
        """SELECT COUNT(DISTINCT user_id) as count FROM (
            SELECT user_id FROM orders WHERE created_at > datetime('now', '-7 days')
            UNION
            SELECT user_id FROM active_shoppers WHERE last_activity > datetime('now', '-7 days')
        )"""
    )
    row = await cursor.fetchone()
    stats["active_users_7d"] = row["count"]

    # Total successful purchases (paid + shipped + delivered)
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM orders WHERE status IN ('paid', 'shipped', 'delivered')"
    )
    row = await cursor.fetchone()
    stats["successful_purchases"] = row["count"]

    # Total revenue (all paid orders)
    cursor = await db.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE status IN ('paid', 'shipped', 'delivered')"
    )
    row = await cursor.fetchone()
    stats["total_revenue"] = row["total"]

    # Users currently with items in cart
    cursor = await db.execute(
        "SELECT COUNT(DISTINCT user_id) as count FROM cart_items"
    )
    row = await cursor.fetchone()
    stats["users_in_cart"] = row["count"]

    # Abandoned carts (cart items but no orders in last 24h)
    cursor = await db.execute(
        """SELECT COUNT(DISTINCT ci.user_id) as count
           FROM cart_items ci
           LEFT JOIN orders o ON ci.user_id = o.user_id
              AND o.created_at > datetime('now', '-24 hours')
           WHERE o.id IS NULL"""
    )
    row = await cursor.fetchone()
    stats["abandoned_carts"] = row["count"]

    # Pending orders
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM orders WHERE status = 'pending'"
    )
    row = await cursor.fetchone()
    stats["pending_orders"] = row["count"]

    # Total orders
    cursor = await db.execute("SELECT COUNT(*) as count FROM orders")
    row = await cursor.fetchone()
    stats["total_orders"] = row["count"]

    # Total products
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM products WHERE is_active = 1"
    )
    row = await cursor.fetchone()
    stats["total_products"] = row["count"]

    # Total categories
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM categories WHERE is_active = 1"
    )
    row = await cursor.fetchone()
    stats["total_categories"] = row["count"]

    return stats


async def get_all_products_admin(search_query: str = None):
    """Get all active products for admin list with optional search."""
    db = await get_db()
    if search_query:
        cursor = await db.execute(
            """SELECT p.*, c.name as category_name,
                      (SELECT quantity FROM cart_items WHERE product_id = p.id) as cart_reserved
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.id
               WHERE p.is_active = 1 AND (p.name LIKE ? OR p.description LIKE ?)
               ORDER BY p.created_at DESC""",
            (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor = await db.execute(
            """SELECT p.*, c.name as category_name,
                      (SELECT COALESCE(SUM(quantity), 0) FROM cart_items WHERE product_id = p.id) as cart_reserved
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.id
               WHERE p.is_active = 1
               ORDER BY p.created_at DESC"""
        )
    return await cursor.fetchall()


async def get_product_stock(product_id: int):
    """Get current stock for a product."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT stock FROM products WHERE id = ?", (product_id,)
    )
    row = await cursor.fetchone()
    return row["stock"] if row else 0


async def update_product_stock(product_id: int, new_stock: int):
    """Directly set product stock."""
    db = await get_db()
    await db.execute(
        "UPDATE products SET stock = ? WHERE id = ?",
        (new_stock, product_id)
    )
    await db.commit()


async def get_recent_orders(limit: int = 10):
    """Get recent orders with user info for admin view."""
    db = await get_db()
    cursor = await db.execute(
        """SELECT o.*, u.telegram_id, u.username, u.full_name
           FROM orders o
           LEFT JOIN users u ON o.user_id = u.id
           ORDER BY o.created_at DESC
           LIMIT ?""",
        (limit,)
    )
    return await cursor.fetchall()


async def get_total_products_count():
    """Count active products."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM products WHERE is_active = 1"
    )
    row = await cursor.fetchone()
    return row["count"]


async def search_users(query: str):
    """Search users by name or username."""
    db = await get_db()
    cursor = await db.execute(
        """SELECT * FROM users
           WHERE full_name LIKE ? OR username LIKE ? OR telegram_id LIKE ?
           ORDER BY created_at DESC LIMIT 20""",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    )
    return await cursor.fetchall()
