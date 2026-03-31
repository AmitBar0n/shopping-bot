import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from config import AUTHORIZED_IDS, NAMES
import database as db
import keyboards as kb
import notifications as notif
from suggestions import get_suggestions

logger = logging.getLogger(__name__)

AWAITING_ITEM_NAME = 1
AWAITING_CATEGORY_NAME = 2
AWAITING_CATEGORY_EMOJI = 3


def get_user_name(user_id: int) -> str:
    return NAMES.get(user_id, str(user_id))


async def auth_check(update: Update) -> bool:
    if update.effective_user.id not in AUTHORIZED_IDS:
        await update.effective_message.reply_text("אין לך גישה לבוט הזה.")
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await auth_check(update):
        return
    name = get_user_name(update.effective_user.id)
    await update.message.reply_text(
        f"שלום {name}! 🛒 רשימת הקניות של עמית וירדן",
        reply_markup=kb.main_menu(),
    )


async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    items = await db.get_all_items()
    if not items:
        await query.edit_message_text(
            "הרשימה ריקה! לחצו ➕ כדי להוסיף פריטים.",
            reply_markup=kb.main_menu(),
        )
        return
    grouped: dict[str, list] = {}
    for item in items:
        key = f"{item['emoji']} {item['category_name']}"
        grouped.setdefault(key, []).append(item["name"])
    lines = ["🛒 *רשימת הקניות*\n"]
    for cat_label, item_names in grouped.items():
        lines.append(f"*{cat_label}*")
        for n in item_names:
            lines.append(f"  • {n}")
        lines.append("")
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=kb.main_menu(),
    )


# ── Add item flow ──────────────────────────────────────────────

async def add_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    categories = await db.get_all_categories()
    await query.edit_message_text(
        "בחר קטגוריה:", reply_markup=kb.category_picker(categories, action="pick_cat")
    )
    return AWAITING_ITEM_NAME


async def category_picked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.split(":")[1])
    categories = await db.get_all_categories()
    cat = next((c for c in categories if c["id"] == cat_id), None)
    if not cat:
        await query.edit_message_text("קטגוריה לא נמצאה.", reply_markup=kb.main_menu())
        return ConversationHandler.END
    context.user_data["selected_category_id"] = cat_id
    context.user_data["selected_category_name"] = cat["name"]
    context.user_data["selected_category_emoji"] = cat["emoji"]

    suggestions = get_suggestions(cat["name"])
    if suggestions:
        await query.edit_message_text(
            f"בחר פריט ל-{cat['emoji']} {cat['name']}:",
            reply_markup=kb.item_suggestions(suggestions, cat_id),
        )
    else:
        await query.edit_message_text(f"כתוב את שם הפריט עבור {cat['emoji']} {cat['name']}:")
    return AWAITING_ITEM_NAME


async def suggestion_picked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User tapped a suggestion button."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":", 2)  # suggest:cat_id:item_name
    cat_id = int(parts[1])
    item_name = parts[2]

    categories = await db.get_all_categories()
    cat = next((c for c in categories if c["id"] == cat_id), None)
    cat_name = cat["name"] if cat else ""
    cat_emoji = cat["emoji"] if cat else ""
    user_name = get_user_name(update.effective_user.id)

    try:
        await db.add_item(cat_id, item_name, user_name)
    except db.DuplicateItemError:
        await query.edit_message_text(
            f"'{item_name}' כבר ברשימה תחת {cat_emoji} {cat_name}!",
            reply_markup=kb.main_menu(),
        )
        return ConversationHandler.END

    await query.edit_message_text(
        f"✅ {item_name} נוסף ל-{cat_emoji} {cat_name}!", reply_markup=kb.main_menu()
    )
    await notif.notify_other(
        update.get_bot(), update.effective_user.id,
        f"{user_name} הוסיף/ה: {item_name} ({cat_emoji} {cat_name})",
    )
    return ConversationHandler.END


async def custom_type_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User clicked 'הקלד בעצמך'."""
    query = update.callback_query
    await query.answer()
    cat_emoji = context.user_data.get("selected_category_emoji", "")
    cat_name = context.user_data.get("selected_category_name", "")
    await query.edit_message_text(f"כתוב את שם הפריט עבור {cat_emoji} {cat_name}:")
    return AWAITING_ITEM_NAME


async def item_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await auth_check(update):
        return ConversationHandler.END
    name = update.message.text.strip()
    cat_id = context.user_data.get("selected_category_id")
    cat_name = context.user_data.get("selected_category_name", "")
    cat_emoji = context.user_data.get("selected_category_emoji", "")
    user_name = get_user_name(update.effective_user.id)
    try:
        await db.add_item(cat_id, name, user_name)
    except db.DuplicateItemError:
        await update.message.reply_text(
            f"'{name}' כבר ברשימה תחת {cat_emoji} {cat_name}!",
            reply_markup=kb.main_menu(),
        )
        return ConversationHandler.END
    await update.message.reply_text(
        f"✅ {name} נוסף ל-{cat_emoji} {cat_name}!", reply_markup=kb.main_menu()
    )
    await notif.notify_other(
        update.get_bot(), update.effective_user.id,
        f"{user_name} הוסיף/ה: {name} ({cat_emoji} {cat_name})",
    )
    return ConversationHandler.END


# ── Remove item flow ───────────────────────────────────────────

async def remove_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    items = await db.get_all_items()
    if not items:
        await query.edit_message_text("הרשימה ריקה.", reply_markup=kb.main_menu())
        return
    removal_action = "mark_done" if query.data == "done_start" else "delete_item"
    await query.edit_message_text(
        "בחר פריט:", reply_markup=kb.items_list_for_removal(items, action=removal_action)
    )


async def item_removed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    action, item_id = parts[0], int(parts[1])
    item = await db.get_item_by_id(item_id)
    if not item:
        await query.edit_message_text("הפריט כבר הוסר.", reply_markup=kb.main_menu())
        return
    await db.delete_item(item_id)
    user_name = get_user_name(update.effective_user.id)
    if action == "mark_done":
        msg = f"✅ {item['name']} סומן כנקנה!"
        notif_msg = f"{user_name} סימן/ה כנקנה: {item['name']} ({item['emoji']} {item['category_name']})"
    else:
        msg = f"🗑️ {item['name']} הוסר מהרשימה."
        notif_msg = f"{user_name} מחק/ה: {item['name']} ({item['emoji']} {item['category_name']})"
    await query.edit_message_text(msg, reply_markup=kb.main_menu())
    await notif.notify_other(update.get_bot(), update.effective_user.id, notif_msg)


# ── Manage categories flow ─────────────────────────────────────

async def manage_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("ניהול קטגוריות:", reply_markup=kb.manage_categories_menu())


async def add_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("כתוב את שם הקטגוריה החדשה:")
    return AWAITING_CATEGORY_NAME


async def category_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await auth_check(update):
        return ConversationHandler.END
    context.user_data["new_category_name"] = update.message.text.strip()
    await update.message.reply_text("כתוב אמוג'י לקטגוריה (לדוגמה: 🧊):")
    return AWAITING_CATEGORY_EMOJI


async def category_emoji_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await auth_check(update):
        return ConversationHandler.END
    name = context.user_data.get("new_category_name", "")
    emoji = update.message.text.strip()
    await db.add_category(name, emoji)
    await update.message.reply_text(
        f"✅ הקטגוריה {emoji} {name} נוספה!", reply_markup=kb.main_menu()
    )
    return ConversationHandler.END


async def delete_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    categories = await db.get_all_categories()
    deletable = [c for c in categories if not c["is_default"]]
    if not deletable:
        await query.edit_message_text(
            "אין קטגוריות מותאמות אישית למחיקה.", reply_markup=kb.manage_categories_menu()
        )
        return
    await query.edit_message_text(
        "בחר קטגוריה למחיקה (ריקות בלבד):", reply_markup=kb.categories_for_deletion(categories)
    )


async def category_deleted(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.split(":")[1])
    try:
        await db.delete_category(cat_id)
        await query.edit_message_text("✅ הקטגוריה נמחקה.", reply_markup=kb.main_menu())
    except db.CategoryNotEmptyError:
        await query.edit_message_text(
            "לא ניתן למחוק קטגוריה עם פריטים. הסר קודם את הפריטים.",
            reply_markup=kb.main_menu(),
        )
    except db.CategoryProtectedError:
        await query.edit_message_text(
            "לא ניתן למחוק קטגוריית ברירת מחדל.", reply_markup=kb.main_menu()
        )


# ── Cancel / Back ──────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("בוטל.", reply_markup=kb.main_menu())
    return ConversationHandler.END


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("תפריט ראשי:", reply_markup=kb.main_menu())


# ── ConversationHandler factories ─────────────────────────────

def add_item_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_item_start, pattern="^add_item_start$")],
        states={
            AWAITING_ITEM_NAME: [
                CallbackQueryHandler(category_picked, pattern="^pick_cat:"),
                CallbackQueryHandler(suggestion_picked, pattern="^suggest:"),
                CallbackQueryHandler(custom_type_start, pattern="^custom_type:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, item_name_received),
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")],
    )


def add_category_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_category_start, pattern="^add_category_start$")],
        states={
            AWAITING_CATEGORY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, category_name_received),
            ],
            AWAITING_CATEGORY_EMOJI: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, category_emoji_received),
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")],
    )
