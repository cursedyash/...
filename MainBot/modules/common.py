from telegram import Update
from telegram.ext import ContextTypes
import time
import MainBot.modules.mongo.upload as uploads
from MainBot import (
    application,
    BOT_USERNAME,
    OWNER_ID,
    FORCE_SUB,
    MAIN_CHANNEL,
    FIRST_NAMES,
    BATCH_FILES,
)
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from MainBot.modules.helper_funcs.chat_status import (
    admin_command,
)
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.constants import ParseMode
from MainBot.modules.helper_funcs.chat_status import is_user_in_chat
from telegram.helpers import mention_html
import html
from MainBot.modules.users import log_user
from MainBot.modules.helper_funcs.helper import send_message_to_chat, reply_to_message


async def send_user_file(update: Update, context: ContextTypes.DEFAULT_TYPE, arg):
    user = update.effective_user
    message = update.effective_message
    try:
        resp = await uploads.get_file(arg)
    except:
        resp = []
    if resp:
        for el in resp:
            await context.bot.copy_message(user.id, MAIN_CHANNEL, el)
    else:
        msg = "Unable to get that file!"
        await message.reply_text(msg)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await log_user(update, context)
    args = context.args
    user = update.effective_user
    first_name = user.first_name
    message = update.effective_message
    if update.effective_chat.type != "private":
        message.reply_text("Message me personally!")
        return
    if len(args) > 0:
        await send_user_file(update, context, args[0])
    else:
        try:
            if await part_of_force_sub(context.bot, user.id):
                msg = "<b>👋 Hey, {}\n\nI can store private files in Specified Channel and other users can access it from special link.</b>".format(
                    mention_html(int(user.id), html.escape(first_name)),
                )
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "About Me", callback_data="start_message_about"
                            ),
                            InlineKeyboardButton(
                                "Close",
                                callback_data="start_message_close",
                            ),
                        ],
                    ]
                )
            else:
                msg = "<b>👋 Hey, {}\n\nYou need to join in my Channel/Group to use me\n\nKindly Please join Channel</b>".format(
                    mention_html(int(user.id), html.escape(first_name)),
                )
                if FORCE_SUB["id"] != "":
                    invite_link = await context.bot.createChatInviteLink(
                        int(FORCE_SUB["id"])
                    )
                    invite_link = invite_link.invite_link
                    keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=f"Join Channel ⛵️",
                                    url=f"{invite_link}",
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Try Again 🔄",
                                    callback_data="start_message_tryagain",
                                )
                            ],
                        ]
                    )
                else:
                    keyboard = None
            await send_message_to_chat(
                msg,
                context.bot,
                user.id,
                ParseMode.HTML,
                keyboard,
            )
        except Exception as e:
            print(e)
            msg = "I am unable to create chat invite link, please contact admins!"
            await send_message_to_chat(
                msg,
                context.bot,
                user.id,
            )
            await send_message_to_chat(
                "I am unable to create invite link for the force sub channel, please make sure i am admin with proper rights!",
                context.bot,
                OWNER_ID,
            )


async def start_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data.split("_")
    from_user_id = str(query.from_user.id)
    typee = callback_data[2]
    if typee == "about":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Close",
                        callback_data="start_message_close",
                    )
                ]
            ]
        )
        await query.edit_message_text(
            "Owner : {}".format(mention_html(int(OWNER_ID), OWNER_ID)),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    elif typee == "tryagain":
        try:
            if await part_of_force_sub(context.bot, from_user_id):
                msg = "<b>👋 Hey, {}\n\nI can store private files in Specified Channel and other users can access it from special link.</b>".format(
                    mention_html(
                        int(from_user_id),
                        html.escape(FIRST_NAMES.get(from_user_id, "None")),
                    ),
                )
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "About Me", callback_data="start_message_about"
                            ),
                            InlineKeyboardButton(
                                "Close",
                                callback_data="start_message_close",
                            ),
                        ],
                    ]
                )
            else:
                await query.answer("You need to join the channel first!")
                return
            await query.edit_message_text(
                msg,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except Exception as e:
            print(e)
            msg = "I am unable to create chat invite link, please contact admins!"
            await send_message_to_chat(
                msg,
                context.bot,
                from_user_id,
            )
            await send_message_to_chat(
                "I am unable to create invite link for the force sub channel, please make sure i am admin with proper rights!",
                context.bot,
                OWNER_ID,
            )
    else:
        await query.message.delete()


FALLBACK_STATE = 0
FIRST_INPUT_BATCH = 1
SECOND_INPUT_BATCH = 2


async def part_of_force_sub(bot, user_id):
    try:
        chat_id = int(FORCE_SUB["id"])
        if chat_id != "":
            if not await is_user_in_chat(bot, chat_id, int(user_id)):
                return False
        return True
    except:
        return False


@admin_command
async def batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    user_id = str(user.id)
    if not await part_of_force_sub(context.bot, user.id):
        await start(update, context)
        return
    msg = "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link\n\nUse /cancel to cancel current process"
    await reply_to_message(message, msg, context.bot, update.effective_chat.id)
    context.chat_data[user_id] = {}
    BATCH_FILES["status"] = True
    return FIRST_INPUT_BATCH


async def handle_first_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    command = update.message.text
    user = update.effective_user
    user_id = str(user.id)
    if command and command[0] == "/":
        if command == "/cancel":
            await reply_to_message(
                message,
                "You Have Canceled The current Request.",
                context.bot,
                update.effective_chat.id,
            )
        else:
            await reply_to_message(
                message,
                "You had a batch request ongoing, I have cancelled it for now.\n\nYou can use your command again.",
                context.bot,
                update.effective_chat.id,
            )
        BATCH_FILES["status"] = False
        return ConversationHandler.END
    else:
        # print(message)
        valid = False
        if command:
            main_channel_id = str(MAIN_CHANNEL)[4:]
            print(main_channel_id)
            if main_channel_id in command:
                start_ = int(list(command.split(main_channel_id + "/"))[1])
                context.chat_data[user_id]["start"] = start_
                valid = True
        else:
            if int(message.forward_from_chat.id) == int(MAIN_CHANNEL):
                start_ = message.forward_from_message_id
                context.chat_data[user_id]["start"] = start_
                valid = True
        if valid:
            msg = "Forward the Last Message from DB Channel (with Quotes)..\n\nOr Send the DB Channel Post link\n\nUse /cancel to cancel the request"
            await reply_to_message(
                message,
                msg,
                context.bot,
                update.effective_chat.id,
            )
            return SECOND_INPUT_BATCH
        else:
            msg = "❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel\n\nUse /cancel to cancel the request"
            await reply_to_message(
                message,
                msg,
                context.bot,
                update.effective_chat.id,
            )
            return FIRST_INPUT_BATCH


async def handle_second_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    command = update.message.text
    user = update.effective_user
    user_id = str(user.id)
    if command and command[0] == "/":
        if command == "/cancel":
            await reply_to_message(
                message,
                "You Have Canceled The current Request.",
                context.bot,
                update.effective_chat.id,
            )
        else:
            await reply_to_message(
                message,
                "You had a batch request ongoing, I have cancelled it for now.\n\nYou can use your command again.",
                context.bot,
                update.effective_chat.id,
            )
        BATCH_FILES["status"] = False
        return ConversationHandler.END
    else:
        valid = False
        if command:
            main_channel_id = str(MAIN_CHANNEL)[4:]
            print(main_channel_id)
            if main_channel_id in command:
                end_ = int(list(command.split(main_channel_id + "/"))[1])
                if (
                    (user_id not in context.chat_data)
                    or ("start" not in context.chat_data[user_id])
                    or (context.chat_data[user_id]["start"] > end_)
                ):
                    valid = False
                else:
                    context.chat_data[user_id]["end"] = end_
                    valid = True
        else:
            if int(message.forward_from_chat.id) == int(MAIN_CHANNEL):
                end_ = message.forward_from_message_id
                if (
                    (user_id not in context.chat_data)
                    or ("start" not in context.chat_data[user_id])
                    or (context.chat_data[user_id]["start"] > end_)
                ):
                    valid = False
                else:
                    context.chat_data[user_id]["end"] = end_
                    valid = True
        if valid:
            valid_, uid, count = await uploads.upload_multiple_files(
                context.chat_data[user_id]["start"],
                context.chat_data[user_id]["end"],
                context.bot,
            )
            if valid_:
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
                    "Unable to create links for these files, please try again properly.",
                    context.bot,
                    update.effective_chat.id,
                )
            BATCH_FILES["status"] = False
            return ConversationHandler.END
        else:
            msg = "❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel"
            await reply_to_message(
                message,
                msg,
                context.bot,
                update.effective_chat.id,
            )
            return SECOND_INPUT_BATCH


START_HANDLER = CommandHandler("start", start)
USERCOMMAND_START_CONV_HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler("batch", batch),
    ],
    states={
        FIRST_INPUT_BATCH: [
            MessageHandler(
                filters.Regex(r"^https://t\.me/") | filters.COMMAND | filters.FORWARDED,
                handle_first_input,
            ),
        ],
        SECOND_INPUT_BATCH: [
            MessageHandler(
                filters.Regex(r"^https://t\.me/") | filters.COMMAND | filters.FORWARDED,
                handle_second_input,
            ),
        ],
    },
    fallbacks=[],
)
CHATS_TOGGLE_QUERY_HANDLER = CallbackQueryHandler(
    start_message_callback, pattern="start_message_.*"
)
application.add_handler(START_HANDLER)
application.add_handler(USERCOMMAND_START_CONV_HANDLER)
application.add_handler(CHATS_TOGGLE_QUERY_HANDLER)

__mod_name__ = "Common"
__handlers__ = [
    START_HANDLER,
    USERCOMMAND_START_CONV_HANDLER,
    CHATS_TOGGLE_QUERY_HANDLER,
]
