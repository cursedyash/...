from functools import wraps
from MainBot import ADMINS, OWNER_ID
from telegram import Update
from MainBot.modules.helper_funcs.helper import reply_to_message
from telegram.ext import ContextTypes


def owner_command(func):
    @wraps(func)
    async def is_owner(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = update.effective_user
        message = update.effective_message
        user_id = str(user.id)
        if user_id == OWNER_ID:
            return await func(update, context, *args, **kwargs)
        else:
            await reply_to_message(
                message,
                "You are not allowed to use this.",
                context.bot,
                update.effective_chat.id,
            )

    return is_owner


def admin_command(func):
    @wraps(func)
    async def is_owner(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = update.effective_user
        message = update.effective_message
        user_id = str(user.id)
        if user_id in ADMINS:
            return await func(update, context, *args, **kwargs)
        else:
            await reply_to_message(
                message,
                "You are not allowed to use this.",
                context.bot,
                update.effective_chat.id,
            )

    return is_owner


async def is_user_in_chat(bot, chat, user_id):
    try:
        member = await bot.get_chat_member(chat, user_id)
        if member:
            return member.status not in ("left", "kicked", "banned")
        return False
    except:
        return False
