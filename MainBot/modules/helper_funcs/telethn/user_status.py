from MainBot.modules.helper_funcs.telethn import GREAT_USERS, telethnn
from MainBot import ADMINS
from telethon.tl.types import ChannelParticipantsAdmins
from telethon import functions


async def get_user_about(user_id):
    try:
        full = await telethnn(functions.users.GetFullUserRequest(int(user_id)))
        if full:
            bio = full.full_user.about
            if not bio:
                return "No Bio"
            return bio
        return "Nothing Found"
    except Exception as e:
        pass


async def send_message(user_id, message):
    try:
        await telethnn.send_message(int(user_id), message, parse_mode="markdown")
    except Exception as e:
        pass


async def user_is_ban_protected(user_id: int, message):
    status = False
    if message.chat.type == "private" or user_id in (GREAT_USERS):
        return True

    async for user in telethnn.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id:
            status = True
            break
    return status


async def user_is_admin(user_id: int, message):
    status = False
    if message.chat.type == "private":
        return True
    async for user in telethnn.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in ADMINS:
            status = True
            break
    return status


async def is_user_admin(user_id: int, chat_id):
    status = False
    async for user in telethnn.iter_participants(
        chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in ADMINS:
            status = True
            break
    return status


async def get_chat_admins(chat_id):
    admins = []
    async for user in telethnn.iter_participants(
        chat_id, filter=ChannelParticipantsAdmins
    ):
        admins.append(str(user.id))
    return admins


async def bot_is_admin(chat_id: int):
    status = False
    thor = await telethnn.get_me()
    async for user in telethnn.iter_participants(
        chat_id, filter=ChannelParticipantsAdmins
    ):
        if thor.id == user.id:
            status = True
            break
    return status


async def is_user_in_chat(chat_id, user_id):
    status = False
    try:
        async for user in telethnn.iter_participants(chat_id):
            if str(user_id) == str(user.id):
                status = True
                break
        async for user in telethnn.iter_participants(
            chat_id, filter=ChannelParticipantsAdmins
        ):
            if str(user_id) == str(user.id):
                status = True
                break
    except Exception as e:
        print(e)
    print(status, chat_id)
    return status


async def can_change_info(message):
    status = False
    if message.chat.admin_rights:
        status = message.chat.admin_rights.change_info
    return status


async def can_ban_users(message):
    status = False
    if message.chat.admin_rights:
        status = message.chat.admin_rights.ban_users
    return status


async def can_pin_messages(message):
    status = False
    if message.chat.admin_rights:
        status = message.chat.admin_rights.pin_messages
    return status


async def can_invite_users(message):
    status = False
    if message.chat.admin_rights:
        status = message.chat.admin_rights.invite_users
    return status


async def can_add_admins(message):
    status = False
    if message.chat.admin_rights:
        status = message.chat.admin_rights.add_admins
    return status


async def can_delete_messages(message):
    if message.is_private:
        return True
    elif message.chat.admin_rights:
        status = message.chat.admin_rights.delete_messages
        return status
    else:
        return False
