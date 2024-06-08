import importlib
from MainBot import (
    LOGGER,
    application,
    FIRST_NAMES,
    ERROR_LOGS,
    LOGGER,
    CURRENT_USERS,
    TOKEN,
    FORCE_SUB,
)
import traceback
import json
import MainBot.modules.mongo.users as users
import MainBot.modules.mongo.extra_stuff as extra_stuff
from MainBot.modules import ALL_MODULES
from telegram import Update
import html
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
)
from telegram.constants import ParseMode
from sys import argv

IMPORTED = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("MainBot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")


def load_force_sub_channel():
    force_sub = extra_stuff.get_force_sub()
    if not force_sub:
        extra_stuff.add_force_sub(FORCE_SUB["id"])
    else:
        FORCE_SUB["id"] = str(force_sub["id"])


def load_user_first_names():
    CURR_USER_FIRST_NAMES = users.get_all_users()
    for el in CURR_USER_FIRST_NAMES:
        FIRST_NAMES[el] = CURR_USER_FIRST_NAMES[el]["first_name"]


def load_all_users():
    all_users = users.get_all_users()
    for el in all_users:
        CURRENT_USERS.add(el)


def extract_user(content):
    data = list(content.split("@"))
    return data[0], data[1]


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    LOGGER.error("Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    await context.bot.send_message(
        chat_id=ERROR_LOGS, text=message, parse_mode=ParseMode.HTML
    )


def main() -> None:
    application.add_error_handler(error_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    load_user_first_names()
    load_all_users()
    load_force_sub_channel()
    main()
