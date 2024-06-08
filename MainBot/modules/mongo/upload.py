import threading
from MainBot.modules.mongo import db
from MainBot.modules.helper_funcs.helper import (
    send_message_to_chat,
    generate_random_file_id,
)
from MainBot import MAIN_CHANNEL, BOT_USERNAME
from telegram.constants import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

UPLOAD_COLLECTION = db["upload"]
INSERTION_LOCK = threading.RLock()


async def upload_file(msg_, bot):
    with INSERTION_LOCK:
        try:
            msg_id = await msg_.copy(MAIN_CHANNEL)
            uid = generate_random_file_id()
            curr = UPLOAD_COLLECTION.find_one({"uid": uid})
            while curr:
                uid = generate_random_file_id()
                curr = UPLOAD_COLLECTION.find_one({"uid": uid})
            file_link = f"https://t.me/{BOT_USERNAME}?start={uid}"
            file_share_link = f"https://telegram.me/share/url?url={file_link}"
            keyboard = [
                [
                    InlineKeyboardButton(
                        text=f"Share Link [1]🔗",
                        url=f"{file_share_link}",
                    )
                ]
            ]
            document = {"msg_ids": [msg_id.message_id], "uid": uid}
            UPLOAD_COLLECTION.insert_one(document)
            await send_message_to_chat(
                file_link,
                bot,
                MAIN_CHANNEL,
                ParseMode.MARKDOWN,
                InlineKeyboardMarkup(keyboard),
            )

            return True, uid, 1
        except Exception as e:
            return False, "", 0


async def get_file(uid):
    curr = UPLOAD_COLLECTION.find_one({"uid": uid})
    if curr:
        return curr["msg_ids"]
    return []


async def upload_multiple_files(start_, end_, bot):
    with INSERTION_LOCK:
        try:
            uid = generate_random_file_id()
            curr = UPLOAD_COLLECTION.find_one({"uid": uid})
            while curr:
                uid = generate_random_file_id()
                curr = UPLOAD_COLLECTION.find_one({"uid": uid})
            file_link = f"https://t.me/{BOT_USERNAME}?start={uid}"
            file_share_link = f"https://telegram.me/share/url?url={file_link}"
            document = {"msg_ids": [i for i in range(start_, end_ + 1)], "uid": uid}
            n = len(document["msg_ids"])
            keyboard = [
                [
                    InlineKeyboardButton(
                        text=f"Share Link [{n}]🔗",
                        url=f"{file_share_link}",
                    )
                ]
            ]
            UPLOAD_COLLECTION.insert_one(document)
            await send_message_to_chat(
                file_link,
                bot,
                MAIN_CHANNEL,
                ParseMode.MARKDOWN,
                InlineKeyboardMarkup(keyboard),
            )
            return True, uid, n
        except Exception as e:
            return False, "", 0
