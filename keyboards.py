from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 הצג רשימה", callback_data="show_list")],
        [InlineKeyboardButton("➕ הוסף פריט", callback_data="add_item_start")],
        [InlineKeyboardButton("⚙️ נהל קטגוריות", callback_data="manage_categories")],
    ])


def category_picker(categories: list[dict], action: str) -> InlineKeyboardMarkup:
    rows = []
    for cat in categories:
        label = f"{cat['emoji']} {cat['name']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"{action}:{cat['id']}")])
    rows.append([InlineKeyboardButton("❌ ביטול", callback_data="cancel")])
    return InlineKeyboardMarkup(rows)


def items_list_for_removal(items: list[dict], action: str) -> InlineKeyboardMarkup:
    rows = []
    for item in items:
        label = f"{item['emoji']} {item['name']} ({item['category_name']})"
        rows.append([InlineKeyboardButton(label, callback_data=f"{action}:{item['id']}")])
    rows.append([InlineKeyboardButton("❌ ביטול", callback_data="cancel")])
    return InlineKeyboardMarkup(rows)


def manage_categories_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ הוסף קטגוריה", callback_data="add_category_start")],
        [InlineKeyboardButton("🗑️ מחק קטגוריה", callback_data="delete_category_start")],
        [InlineKeyboardButton("🔙 חזור", callback_data="back_to_main")],
    ])


def categories_for_deletion(categories: list[dict]) -> InlineKeyboardMarkup:
    deletable = [c for c in categories if not c["is_default"]]
    rows = []
    for cat in deletable:
        label = f"{cat['emoji']} {cat['name']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"delete_cat:{cat['id']}")])
    rows.append([InlineKeyboardButton("❌ ביטול", callback_data="cancel")])
    return InlineKeyboardMarkup(rows)
