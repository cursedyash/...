import threading
from MainBot.modules.mongo import db

USERS_COLLECTION = db["users"]
CHATS_COLLECTION = db["chats"]
INSERTION_LOCK = threading.RLock()


def set_user(user_id, first=None, last=None, username=None):
    with INSERTION_LOCK:
        curr = USERS_COLLECTION.find_one({"user_id": user_id})
        if not curr:
            document = {
                "user_id": user_id,
                "first_name": first,
                "last_name": last,
                "user_name": username,
            }
            USERS_COLLECTION.insert_one(document)
        else:
            curr["first_name"] = first
            curr["last_name"] = last
            curr["user_name"] = username
            USERS_COLLECTION.update_one({"user_id": user_id}, {"$set": curr})
        return True


def set_chat(chat_id, name=None, username=None):
    with INSERTION_LOCK:
        curr = CHATS_COLLECTION.find_one({"chat_id": chat_id})
        if not curr:
            document = {
                "chat_id": chat_id,
                "name": name,
                "user_name": username,
            }
            CHATS_COLLECTION.insert_one(document)
        else:
            curr["name"] = name
            curr["user_name"] = username
            CHATS_COLLECTION.update_one({"chat_id": chat_id}, {"$set": curr})
        return True


def get_user(user_id):
    curr = USERS_COLLECTION.find_one({"user_id": user_id})
    if not curr:
        return None
    else:
        return curr


def get_username(user_id):
    curr = USERS_COLLECTION.find_one({"user_id": user_id})
    if not curr:
        return None
    else:
        return curr["user_name"]


def get_firstname(user_id):
    curr = USERS_COLLECTION.find_one({"user_id": user_id})
    if not curr:
        return None
    else:
        return curr["first_name"]


def get_lastname(user_id):
    curr = USERS_COLLECTION.find_one({"user_id": user_id})
    if not curr:
        return None
    else:
        return curr["last_name"]


def get_userid(user_name):
    curr = USERS_COLLECTION.find_one({"user_name": user_name})
    if not curr:
        return None
    else:
        return curr["user_id"]


def get_all_users():
    all_users = USERS_COLLECTION.find()
    ALL_USERS_LIST = {
        user["user_id"]: {
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "user_name": user.get("user_name", ""),
        }
        for user in all_users
    }
    return ALL_USERS_LIST


def get_all_users_count():
    all_users = USERS_COLLECTION.find()
    return len(all_users)


def get_all_chats():
    all_chats = CHATS_COLLECTION.find()
    ALL_CHATS_LIST = {
        user["chat_id"]: {
            "name": user.get("name", ""),
            "user_name": user.get("user_name", ""),
        }
        for user in all_chats
    }
    return ALL_CHATS_LIST


def get_chats_with_index(index, amount):
    all_chats = CHATS_COLLECTION.find()
    try:
        all_chats_list = list(all_chats)
    except:
        all_chats_list = [el for el in all_chats]
    if len(all_chats_list) <= amount * index:
        return []
    return all_chats_list[amount * index : amount * (index + 1)]


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = CHATS_COLLECTION.find_one_and_update(
            {"chat_id": old_chat_id},
            {"$set": {"chat_id": new_chat_id}},
            return_document=True,
        )
        if not chat:
            chat = {"chat_id": new_chat_id, "name": "", "username": ""}
            CHATS_COLLECTION.insert_one(chat)


def clean_chats(bot):
    all_chats = get_all_chats()
    count = 0
    with INSERTION_LOCK:
        for el in all_chats:
            try:
                chat = bot.get_chat(el)
                bot_member = chat.get_member(bot.id)
                if not bot_member:
                    CHATS_COLLECTION.delete_one({"chat_id": el})
            except Exception as e:
                CHATS_COLLECTION.delete_one({"chat_id": el})
                count += 1
    return f"Deleted {count} chats from DB."


async def broadcasttag(context, msg_id, chat_id):
    all_users = get_all_users()
    all_chats = get_all_chats()
    users_done = 0
    users_fail = 0
    chats_done = 0
    chats_fail = 0
    for el in all_users:
        try:
            await context.bot.forward_message(
                int(el),
                chat_id,
                msg_id,
            )
            users_done += 1
        except Exception as e:
            users_fail += 1
            pass
    for el in all_chats:
        try:
            await context.bot.forward_message(
                int(el),
                chat_id,
                msg_id,
            )
            chats_done += 1
        except Exception as e:
            chats_fail += 1
            pass
    return f"Broadcast Done!\n\nUsers Done : {users_done}\nUsers Failed : {users_fail}\nChats Done : {chats_done}\nChats Failed : {chats_fail}"


async def broadcast(context, msg_, chat_id):
    all_users = get_all_users()
    all_chats = get_all_chats()
    users_done = 0
    users_fail = 0
    chats_done = 0
    chats_fail = 0
    for el in all_users:
        try:
            await msg_.copy(el)
            users_done += 1
        except Exception as e:
            users_fail += 1
            pass
    for el in all_chats:
        try:
            await msg_.copy(el)
            chats_done += 1
        except Exception as e:
            chats_fail += 1
            pass
    return f"Broadcast Done!\n\nUsers Done : {users_done}\nUsers Failed : {users_fail}\nChats Done : {chats_done}\nChats Failed : {chats_fail}"
