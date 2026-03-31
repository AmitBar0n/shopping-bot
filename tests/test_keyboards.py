import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import keyboards as kb

SAMPLE_CATEGORIES = [
    {"id": 1, "name": "ירקות", "emoji": "🥦", "is_default": True, "sort_order": 0},
    {"id": 2, "name": "פירות", "emoji": "🍎", "is_default": True, "sort_order": 1},
]

SAMPLE_ITEMS = [
    {"id": 10, "name": "עגבניות", "category_id": 1, "category_name": "ירקות", "emoji": "🥦", "added_by": "עמית", "added_at": "2024-01-01"},
    {"id": 11, "name": "בננות", "category_id": 2, "category_name": "פירות", "emoji": "🍎", "added_by": "ירדן", "added_at": "2024-01-01"},
]


def test_main_menu_has_three_buttons():
    markup = kb.main_menu()
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(all_buttons) == 3


def test_category_picker_has_one_button_per_category_plus_cancel():
    markup = kb.category_picker(SAMPLE_CATEGORIES, action="add_item")
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(all_buttons) == len(SAMPLE_CATEGORIES) + 1


def test_category_picker_callback_contains_action():
    markup = kb.category_picker(SAMPLE_CATEGORIES, action="add_item")
    first_btn = markup.inline_keyboard[0][0]
    assert "add_item" in first_btn.callback_data


def test_items_list_for_removal_has_correct_count():
    markup = kb.items_list_for_removal(SAMPLE_ITEMS, action="done")
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(all_buttons) == len(SAMPLE_ITEMS) + 1


def test_manage_categories_has_three_buttons():
    markup = kb.manage_categories_menu()
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    assert len(all_buttons) == 3


def test_categories_for_deletion_excludes_defaults():
    cats_with_custom = SAMPLE_CATEGORIES + [
        {"id": 99, "name": "קפואים", "emoji": "🧊", "is_default": False, "sort_order": 9}
    ]
    markup = kb.categories_for_deletion(cats_with_custom)
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    labels = [btn.text for btn in all_buttons]
    assert any("קפואים" in t for t in labels)
    assert not any("ירקות" in t for t in labels)
