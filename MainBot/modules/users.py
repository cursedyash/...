import MainBot.modules.mongo.users as users
from telegram import Update
from MainBot import FIRST_NAMES, CURRENT_USERS, EVENT_LOGS
from telegram.ext import ContextTypes
from telegram.helpers import mention_html
import html
from MainBot.modules.helper_funcs.helper import (
    send_message_to_chat,
)
from telegram.constants import ParseMode


def get_username_from_id(id):
    resp = users.get_username(id)
    return resp


def get_firstname_from_id(id):
    resp = users.get_firstname(id)
    return resp


def get_lastname_from_id(id):
    resp = users.get_lastname(id)
    return resp


def get_id_from_username(username):
    resp = users.get_userid(username)
    return resp


async def log_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message
    if not msg.from_user:
        return
    user_id = str(msg.from_user.id)
    if user_id not in CURRENT_USERS:
        CURRENT_USERS.add(user_id)
        LOG_MSG = "<u>New User</u>\n\nName : {}\nUser Id : {}\nUsername : @{}\nPerm Link : {}\nUser Count : {}".format(
            msg.from_user.first_name,
            user_id,
            msg.from_user.username,
            mention_html(int(user_id), html.escape(msg.from_user.first_name)),
            len(CURRENT_USERS),
        )
        await send_message_to_chat(LOG_MSG, context.bot, EVENT_LOGS, ParseMode.HTML)
    users.set_user(
        user_id,
        msg.from_user.first_name,
        msg.from_user.last_name,
        msg.from_user.username,
    )
    if str(chat.id) != user_id:
        users.set_chat(chat.id, chat.title, chat.username)
    FIRST_NAMES[user_id] = msg.from_user.first_name
    if msg.reply_to_message:
        users.set_user(
            str(msg.reply_to_message.from_user.id),
            msg.reply_to_message.from_user.first_name,
            msg.reply_to_message.from_user.last_name,
            msg.reply_to_message.from_user.username,
        )

    if msg.forward_from:
        users.set_user(
            str(msg.forward_from.id),
            msg.forward_from.first_name,
            msg.forward_from.last_name,
            msg.forward_from.username,
        )

    return "Done"
