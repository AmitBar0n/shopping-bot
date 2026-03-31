from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 הצג רשימה", callback_data="show_list")],
        [InlineKeyboardButton("➕ הוסף פריט", callback_data="add_item_start")],
        [InlineKeyboardButton("⚙️ נהל קטגוריות", callback_data="manage_categories")],
    ])


def list_menu() -> InlineKeyboardMarkup:
    """Menu shown below the shopping list."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ סמן כנקנה", callback_data="done_start"),
            InlineKeyboardButton("🗑️ מחק פריט", callback_data="delete_start"),
        ],
        [InlineKeyboardButton("➕ הוסף פריט", callback_data="add_item_start")],
        [InlineKeyboardButton("🔙 תפריט ראשי", callback_data="back_to_main")],
    ])


def category_picker(categories: list[dict], action: str) -> InlineKeyboardMarkup:
    rows = []
    for cat in categories:
        label = f"{cat['emoji']} {cat['name']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"{action}:{cat['id']}")])
    rows.append([InlineKeyboardButton("❌ ביטול", callback_data="cancel")])
    return InlineKeyboardMarkup(rows)


def item_suggestions(suggestions: list[str], category_id: int) -> InlineKeyboardMarkup:
    """Show suggestion buttons (2 per row) + custom type + cancel."""
    rows = []
    for i in range(0, len(suggestions), 2):
        row = []
        for suggestion in suggestions[i:i+2]:
            row.append(InlineKeyboardButton(
                suggestion,
                callback_data=f"suggest:{category_id}:{suggestion}"
            ))
        rows.append(row)
    rows.append([InlineKeyboardButton("✏️ הקלד בעצמך", callback_data=f"custom_type:{category_id}")])
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
