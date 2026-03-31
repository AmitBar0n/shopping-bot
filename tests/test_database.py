import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
async def mem_db(tmp_path):
    await db.init_db(str(tmp_path / "test.db"))


async def test_default_categories_seeded():
    cats = await db.get_all_categories()
    names = [c["name"] for c in cats]
    assert "ירקות" in names
    assert "פירות" in names
    assert len(cats) == 7


async def test_add_and_get_item():
    cats = await db.get_all_categories()
    cat_id = cats[0]["id"]
    await db.add_item(cat_id, "עגבניות", "עמית")
    items = await db.get_items_by_category(cat_id)
    assert len(items) == 1
    assert items[0]["name"] == "עגבניות"
    assert items[0]["added_by"] == "עמית"


async def test_add_duplicate_item_raises():
    cats = await db.get_all_categories()
    cat_id = cats[0]["id"]
    await db.add_item(cat_id, "עגבניות", "עמית")
    with pytest.raises(db.DuplicateItemError):
        await db.add_item(cat_id, "עגבניות", "ירדן")


async def test_delete_item():
    cats = await db.get_all_categories()
    cat_id = cats[0]["id"]
    await db.add_item(cat_id, "עגבניות", "עמית")
    items = await db.get_items_by_category(cat_id)
    await db.delete_item(items[0]["id"])
    assert await db.get_items_by_category(cat_id) == []


async def test_get_all_items_empty():
    assert await db.get_all_items() == []


async def test_add_custom_category():
    await db.add_category("קפואים", "🧊")
    names = [c["name"] for c in await db.get_all_categories()]
    assert "קפואים" in names


async def test_delete_empty_custom_category():
    await db.add_category("קפואים", "🧊")
    cats = await db.get_all_categories()
    cat = next(c for c in cats if c["name"] == "קפואים")
    await db.delete_category(cat["id"])
    names = [c["name"] for c in await db.get_all_categories()]
    assert "קפואים" not in names


async def test_cannot_delete_default_category():
    cats = await db.get_all_categories()
    default_cat = next(c for c in cats if c["is_default"])
    with pytest.raises(db.CategoryProtectedError):
        await db.delete_category(default_cat["id"])


async def test_cannot_delete_category_with_items():
    await db.add_category("קפואים", "🧊")
    cats = await db.get_all_categories()
    cat = next(c for c in cats if c["name"] == "קפואים")
    await db.add_item(cat["id"], "גלידה", "עמית")
    with pytest.raises(db.CategoryNotEmptyError):
        await db.delete_category(cat["id"])
