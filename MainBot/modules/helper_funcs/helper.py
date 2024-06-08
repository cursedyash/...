from telegram.constants import ParseMode
import random
import secrets
import string


async def reply_to_message(message, text, bot, chat_id, pm=ParseMode.MARKDOWN, rm=None):
    try:
        msgg = await message.reply_text(text, parse_mode=pm, reply_markup=rm)
        return msgg
    except Exception as e:
        print(e)
        msgg = await bot.send_message(chat_id, text, parse_mode=pm, reply_markup=rm)
        return msgg


async def send_message_to_chat(text, bot, chat_id, pm=ParseMode.MARKDOWN, rm=None):
    try:
        await bot.send_message(chat_id, text, parse_mode=pm, reply_markup=rm)
    except Exception as e:
        pass


def generate_random_id():
    random_id = random.randint(10000000, 99999999)
    return random_id


def generate_random_file_id(length=22):
    characters = string.ascii_letters + string.digits
    random_id = "".join(secrets.choice(characters).upper() for _ in range(length))
    return random_id


def capitalize_sentence(sentence):
    return " ".join(word.capitalize() for word in sentence.split())


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time
