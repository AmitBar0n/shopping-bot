import aiosqlite
from datetime import datetime

_db_path = "shopping.db"

DEFAULT_CATEGORIES = [
    ("ירקות", "🥦"),
    ("פירות", "🍎"),
    ("בשר ודגים", "🥩"),
    ("לחמים", "🍞"),
    ("מוצרי חלב", "🥛"),
    ("ניקיון", "🧹"),
    ("רחצה", "🧴"),
]


class DuplicateItemError(Exception):
    pass


class CategoryNotEmptyError(Exception):
    pass


class CategoryProtectedError(Exception):
    pass


async def init_db(path: str = "shopping.db") -> None:
    global _db_path
    _db_path = path
    async with aiosqlite.connect(_db_path) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                emoji TEXT NOT NULL DEFAULT '',
                is_default BOOLEAN NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL REFERENCES categories(id),
                name TEXT NOT NULL,
                added_by TEXT NOT NULL,
                added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor = await conn.execute("SELECT COUNT(*) FROM categories")
        count = (await cursor.fetchone())[0]
        if count == 0:
            for i, (name, emoji) in enumerate(DEFAULT_CATEGORIES):
                await conn.execute(
                    "INSERT INTO categories (name, emoji, is_default, sort_order) VALUES (?, ?, 1, ?)",
                    (name, emoji, i),
                )
        await conn.commit()


async def get_all_categories() -> list[dict]:
    async with aiosqlite.connect(_db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT id, name, emoji, is_default, sort_order FROM categories ORDER BY sort_order, id"
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_all_items() -> list[dict]:
    async with aiosqlite.connect(_db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT i.id, i.name, i.added_by, i.added_at,
                   c.id as category_id, c.name as category_name, c.emoji
            FROM items i
            JOIN categories c ON i.category_id = c.id
            ORDER BY c.sort_order, c.id, i.added_at
        """)
        return [dict(r) for r in await cursor.fetchall()]


async def get_items_by_category(category_id: int) -> list[dict]:
    async with aiosqlite.connect(_db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT id, name, added_by, added_at FROM items WHERE category_id = ? ORDER BY added_at",
            (category_id,),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def add_item(category_id: int, name: str, added_by: str) -> int:
    async with aiosqlite.connect(_db_path) as conn:
        cursor = await conn.execute(
            "SELECT id FROM items WHERE category_id = ? AND LOWER(name) = LOWER(?)",
            (category_id, name),
        )
        if await cursor.fetchone():
            raise DuplicateItemError(f"'{name}' already in category {category_id}")
        cursor = await conn.execute(
            "INSERT INTO items (category_id, name, added_by, added_at) VALUES (?, ?, ?, ?)",
            (category_id, name, added_by, datetime.utcnow().isoformat()),
        )
        await conn.commit()
        return cursor.lastrowid


async def delete_item(item_id: int) -> None:
    async with aiosqlite.connect(_db_path) as conn:
        await conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        await conn.commit()


async def get_item_by_id(item_id: int) -> dict | None:
    async with aiosqlite.connect(_db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT i.id, i.name, i.added_by, c.name as category_name, c.emoji "
            "FROM items i JOIN categories c ON i.category_id = c.id WHERE i.id = ?",
            (item_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_category(name: str, emoji: str) -> int:
    async with aiosqlite.connect(_db_path) as conn:
        cursor = await conn.execute("SELECT MAX(sort_order) FROM categories")
        row = await cursor.fetchone()
        next_order = (row[0] or 0) + 1
        cursor = await conn.execute(
            "INSERT INTO categories (name, emoji, is_default, sort_order) VALUES (?, ?, 0, ?)",
            (name, emoji, next_order),
        )
        await conn.commit()
        return cursor.lastrowid


async def delete_category(category_id: int) -> None:
    async with aiosqlite.connect(_db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT is_default FROM categories WHERE id = ?", (category_id,)
        )
        row = await cursor.fetchone()
        if row and row["is_default"]:
            raise CategoryProtectedError("Cannot delete a default category")
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM items WHERE category_id = ?", (category_id,)
        )
        if (await cursor.fetchone())[0] > 0:
            raise CategoryNotEmptyError("Category has items, cannot delete")
        await conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        await conn.commit()
