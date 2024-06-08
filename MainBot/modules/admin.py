import MainBot.modules.mongo.extra_stuff as extra_stuff
import MainBot.modules.mongo.upload as uploads
import MainBot.modules.mongo.users as users
from telegram import Update
from MainBot import (
    application,
    ADMINS,
    FORCE_SUB,
    CURRENT_USERS,
    StartTime,
    FIRST_NAMES,
    MAIN_CHANNEL,
    BOT_USERNAME,
    BATCH_FILES,
)
from telegram.ext import ContextTypes
import html
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import mention_html
from MainBot.modules.helper_funcs.helper import get_readable_time
from MainBot.modules.helper_funcs.chat_status import (
    admin_command,
    owner_command,
)
import time
import os
import sys
from MainBot.modules.helper_funcs.helper import send_message_to_chat, reply_to_message


@admin_command
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    message = update.message
    args = context.args
    to_user = message.reply_to_message
    msg, Flag = "", False
    if to_user:
        user_to_promote = str(to_user.from_user.id)
    elif len(args) > 0:
        user_to_promote = args[0]
    else:
        user_to_promote = ""
        msg = "Please give some id as well!"
        Flag = True
    if user_to_promote in ADMINS:
        msg = "This member is already a admin"
        Flag = True
    if Flag:
        await reply_to_message(message, msg, context.bot, update.effective_chat.id)
        return
    extra_stuff.add_admin(user_to_promote)
    ADMINS.add(user_to_promote)
    await reply_to_message(
        message,
        f"\nSuccessfully promoted {user_to_promote}!",
        context.bot,
        update.effective_chat.id,
    )
    await send_message_to_chat(
        "You have been promoted to admin by Owner.", context.bot, user_to_promote
    )


@owner_command
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    msg = "<u>Admin List</u>\n\n"
    count = 1
    for el in ADMINS:
        msg += "{}) {} [{}]\n\n".format(
            count, mention_html(int(el), html.escape(FIRST_NAMES.get(el, "None"))), el
        )
    await reply_to_message(
        message,
        msg,
        context.bot,
        update.effective_chat.id,
    )


@owner_command
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    message = update.message
    args = context.args
    to_user = message.reply_to_message
    msg, Flag = "", False
    if to_user:
        user_to_demote = str(to_user.from_user.id)
    elif len(args) > 0:
        user_to_demote = args[0]
    else:
        user_to_demote = ""
        msg = "Please give some id as well!"
        Flag = True
    if user_to_demote not in ADMINS:
        msg = "This member is not an authorized member"
        Flag = True
    if user_to_demote == user_id:
        msg = "You can't demote yourself BAKA!"
        Flag = True
    if Flag:
        await reply_to_message(message, msg, context.bot, update.effective_chat.id)
        return

    if user_to_demote in ADMINS:
        ADMINS.remove(user_to_demote)
        extra_stuff.remove_admin(user_to_demote)
    await reply_to_message(
        message,
        "\nSuccessfully demoted {}!".format(user_to_demote),
        context.bot,
        update.effective_chat.id,
    )
    await send_message_to_chat(
        "You have been demoted by Owner.", context.bot, user_to_demote
    )


@admin_command
async def chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_ = ""
    i = 0
    user_id = str(update.message.from_user.id)
    message = update.message
    if user_id not in ADMINS:
        await message.reply_text("You are not allowed to use that")
        return
    all_chats = users.get_chats_with_index(0, 20)
    for el in all_chats:
        name = ""
        if el["user_name"]:
            name = f"@{el['user_name']}"
        elif el["name"]:
            name = f"{el['name']}"
        msg_ += f"{i+1}) <code>{el['chat_id']}</code> - {html.escape(name)}\n"
        i += 1
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ Previous",
                    callback_data="chat_toggle_back_" + user_id + "_" + "0",
                ),
                InlineKeyboardButton(
                    "Next ➡️",
                    callback_data="chat_toggle_next_" + user_id + "_" + "0",
                ),
            ],
        ]
    )
    await message.reply_text(msg_, reply_markup=keyboard, parse_mode=ParseMode.HTML)


async def toggle_chat_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    from_user_id = str(query.from_user.id)
    callback_data = query.data.split("_")
    typee = callback_data[2]
    user_id = callback_data[3]
    cindex = int(callback_data[4])
    if from_user_id != user_id:
        query.answer("You can't use this.")
        return
    if typee == "back" and cindex == 0:
        query.answer("You can't go back anymore")
        return
    if typee == "back":
        nindex = cindex - 1
    else:
        nindex = cindex + 1
    all_chats = users.get_chats_with_index(nindex, 20)
    if not all_chats:
        if typee == "back":
            query.answer("You can't go back anymore")
        else:
            query.answer("You can't go further anymore")
        return
    msg_ = ""
    i = nindex * 20
    for el in all_chats:
        name = ""
        if el["user_name"]:
            name = f"@{el['user_name']}"
        elif el["name"]:
            name = f"{el['name']}"
        msg_ += f"{i+1}) <code>{el['chat_id']}</code> - {html.escape(name)}\n"
        i += 1

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ Previous",
                    callback_data="chat_toggle_back_" + user_id + "_" + f"{nindex}",
                ),
                InlineKeyboardButton(
                    "Next ➡️",
                    callback_data="chat_toggle_next_" + user_id + "_" + f"{nindex}",
                ),
            ],
        ]
    )
    query.edit_message_text(msg_, parse_mode=ParseMode.HTML, reply_markup=keyboard)


def handle_slash(message):
    if "``" in message:
        arr = list(message.split("``"))
        i = 0
        ret = ""
        for el in arr:
            if i % 2 == 0:
                ret += el
            else:
                ret += "`" + el + "`"
            i += 1
        return ret
    else:
        return message


@admin_command
async def broadcasttag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    reply_to = message.reply_to_message
    if not reply_to:
        await reply_to_message(
            message,
            "Please reply to some message to broadcast.",
            context.bot,
            update.effective_chat.id,
        )
        return
    resp = await users.broadcasttag(
        context, reply_to.message_id, update.effective_chat.id
    )
    await reply_to_message(
        message,
        resp,
        context.bot,
        update.effective_chat.id,
    )


@admin_command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    reply_to = message.reply_to_message
    if not reply_to:
        await reply_to_message(
            message,
            "Please reply to some message to broadcast.",
            context.bot,
            update.effective_chat.id,
        )
        return
    resp = await users.broadcast(context, reply_to, update.effective_chat.id)
    await reply_to_message(
        message,
        resp,
        context.bot,
        update.effective_chat.id,
    )


@admin_command
async def userss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    msg = "<b>Total Users : {}</b>".format(len(CURRENT_USERS))
    await reply_to_message(
        message, msg, context.bot, update.effective_chat.id, ParseMode.HTML
    )


@admin_command
async def setchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    args = update.effective_message.text.split(None, 1)
    if len(args) < 2:
        await reply_to_message(
            message,
            "Please provide valid chat id.",
            context.bot,
            update.effective_chat.id,
        )
        return
    try:
        print(args)
        chat_id = args[1]
        chat = await context.bot.getChat(int(chat_id))
        title = chat.title
        username = chat.username
        first_name = chat.first_name
        last_name = chat.last_name
        invite_link = chat.invite_link
        msg = "Successfully added {} as your force sub channel\n\nId : {}\nFirst Name : {}\nLast Name : {}\nUsername : @{}\nInvite Link : {}".format(
            title, chat_id, first_name, last_name, username, invite_link
        )
        await reply_to_message(
            message,
            msg,
            context.bot,
            update.effective_chat.id,
        )
        extra_stuff.add_force_sub(chat_id)
    except Exception as e:
        print(e)
        await reply_to_message(
            message,
            "It seems i don't have proper rights in that chat or chat id is wrong, please give me proper rights and try again!",
            context.bot,
            update.effective_chat.id,
        )


@admin_command
async def checkchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    try:
        chat_id = FORCE_SUB["id"]
        chat = await context.bot.getChat(int(chat_id))
        title = chat.title
        username = chat.username
        first_name = chat.first_name
        last_name = chat.last_name
        invite_link = chat.invite_link
        msg = "Current Force Sub Channel : {}\n\nId : {}\nFirst Name : {}\nLast Name : {}\nUsername : @{}\nInvite Link : {}".format(
            title, chat_id, first_name, last_name, username, invite_link
        )
        await reply_to_message(
            message,
            msg,
            context.bot,
            update.effective_chat.id,
        )
    except:
        await reply_to_message(
            message,
            "It seems i don't have proper rights in that chat or chat id is wrong, please give me proper rights and try again!",
            context.bot,
            update.effective_chat.id,
        )


@admin_command
async def removeforcesub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if FORCE_SUB["id"] != "":
        msg = f"Successfully removed {FORCE_SUB['id']} from force sub."
    else:
        msg = "Force channel already not set."
    await reply_to_message(
        message,
        msg,
        context.bot,
        update.effective_chat.id,
    )


@admin_command
async def mainchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    try:
        chat_id = MAIN_CHANNEL
        chat = await context.bot.getChat(chat_id)
        title = chat.title
        username = chat.username
        first_name = chat.first_name
        last_name = chat.last_name
        invite_link = chat.invite_link
        msg = "Current Force Sub Channel : {}\n\nId : {}\nFirst Name : {}\nLast Name : {}\nUsername : @{}\nInvite Link : {}".format(
            title, chat_id, first_name, last_name, username, invite_link
        )
        await reply_to_message(
            message,
            msg,
            context.bot,
            update.effective_chat.id,
        )
    except:
        await reply_to_message(
            message,
            "It seems i don't have proper rights in that chat or chat id is wrong, please give me proper rights and try again!",
            context.bot,
            update.effective_chat.id,
        )


@admin_command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = get_readable_time((time.time() - StartTime))
    await reply_to_message(
        update.effective_message,
        "🔨Working Since : </b> <code>{}</code>".format(uptime),
        context.bot,
        update.effective_chat.id,
        parse_mode=ParseMode.HTML,
    )


@admin_command
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if BATCH_FILES["status"]:
        return
    message = update.effective_message
    valid, uid, count = await uploads.upload_file(message, context.bot)
    if valid:
        file_link = f"https://t.me/{BOT_USERNAME}?start={uid}"
        file_share_link = f"https://telegram.me/share/url?url={file_link}"
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"Share Link [{count}]🔗",
                    url=f"{file_share_link}",
                )
            ]
        ]
        await reply_to_message(
            update.effective_message,
            f"*Here is your link*\n\n{file_link}",
            context.bot,
            update.effective_chat.id,
            ParseMode.MARKDOWN,
            InlineKeyboardMarkup(keyboard),
        )
    else:
        await reply_to_message(
            update.effective_message,
            "Unable to upload that file, please try again properly.",
            context.bot,
            update.effective_chat.id,
        )


# UPLOAD_FILE_HANDLER = CommandHandler("upload", upload, block=False)
UPLOAD_FILE_HANDLER = MessageHandler(
    filters.ALL
    & (~filters.COMMAND)
    & (~filters.FORWARDED)
    & (~filters.Regex(r"^https://t\.me/")),
    upload,
)
BROADCAST_HANDLER = CommandHandler("broadcast", broadcast, block=False)
BROADCAST_WITH_TAG_HANDLER = CommandHandler("broadcasttag", broadcasttag, block=False)
USERS_HANDLER = CommandHandler("users", userss)
STATS_HANDLER = CommandHandler("stats", stats)
CHATS_TOGGLE_QUERY_HANDLER = CallbackQueryHandler(
    toggle_chat_list, pattern="chat_toggle_.*"
)
SHOW_CHATS_HANDLER = CommandHandler("chats", chats)
PROMOTE_HANDLER = CommandHandler(["promote", "addadmins"], promote)
DEMOTE_HANDLER = CommandHandler(["demote", "removeadmins"], demote)
ADMIN_LIST_HANDLER = CommandHandler(["adminlist", "admins"], admins)
SET_SUB_CHANNEL_HANDLER = CommandHandler("setchannel", setchannel)
REMOVE_SUB_CHANNEL_HANDLER = CommandHandler("removechannel", removeforcesub)
GET_SUB_CHANNEL_HANDLER = CommandHandler(["getchannel", "checkchannel"], checkchannel)
GET_MAIN_CHANNEL_HANDLER = CommandHandler("mainchannel", mainchannel)
application.add_handler(USERS_HANDLER)
application.add_handler(UPLOAD_FILE_HANDLER)
application.add_handler(BROADCAST_HANDLER)
application.add_handler(STATS_HANDLER)
application.add_handler(PROMOTE_HANDLER)
application.add_handler(DEMOTE_HANDLER)
application.add_handler(CHATS_TOGGLE_QUERY_HANDLER)
application.add_handler(SHOW_CHATS_HANDLER)
application.add_handler(BROADCAST_WITH_TAG_HANDLER)
application.add_handler(ADMIN_LIST_HANDLER)
application.add_handler(SET_SUB_CHANNEL_HANDLER)
application.add_handler(GET_SUB_CHANNEL_HANDLER)
application.add_handler(GET_MAIN_CHANNEL_HANDLER)
application.add_handler(REMOVE_SUB_CHANNEL_HANDLER)

__mod_name__ = "Sudo"
__handlers__ = [
    DEMOTE_HANDLER,
    PROMOTE_HANDLER,
    SHOW_CHATS_HANDLER,
    CHATS_TOGGLE_QUERY_HANDLER,
    BROADCAST_HANDLER,
    STATS_HANDLER,
    BROADCAST_WITH_TAG_HANDLER,
    UPLOAD_FILE_HANDLER,
    USERS_HANDLER,
    ADMIN_LIST_HANDLER,
    SET_SUB_CHANNEL_HANDLER,
    GET_SUB_CHANNEL_HANDLER,
    GET_MAIN_CHANNEL_HANDLER,
    REMOVE_SUB_CHANNEL_HANDLER,
]
