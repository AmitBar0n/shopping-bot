import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from config import BOT_TOKEN
from database import init_db
import handlers as h

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(app: Application) -> None:
    await init_db()
    logger.info("Database ready.")


def build_app() -> Application:
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", h.start))
    app.add_handler(CallbackQueryHandler(h.show_list, pattern="^show_list$"))
    app.add_handler(CallbackQueryHandler(h.back_to_main, pattern="^back_to_main$"))

    app.add_handler(h.add_item_conversation())

    app.add_handler(CallbackQueryHandler(h.remove_item_start, pattern="^done_start$"))
    app.add_handler(CallbackQueryHandler(h.remove_item_start, pattern="^delete_start$"))
    app.add_handler(CallbackQueryHandler(h.item_removed, pattern="^mark_done:"))
    app.add_handler(CallbackQueryHandler(h.item_removed, pattern="^delete_item:"))

    app.add_handler(CallbackQueryHandler(h.manage_categories, pattern="^manage_categories$"))
    app.add_handler(h.add_category_conversation())
    app.add_handler(CallbackQueryHandler(h.delete_category_start, pattern="^delete_category_start$"))
    app.add_handler(CallbackQueryHandler(h.category_deleted, pattern="^delete_cat:"))

    app.add_handler(CallbackQueryHandler(h.cancel, pattern="^cancel$"))

    return app


if __name__ == "__main__":
    logger.info("Bot starting...")
    build_app().run_polling(allowed_updates=["message", "callback_query"])
