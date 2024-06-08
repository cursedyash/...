import logging
import sys
import time
from telethon import TelegramClient
from telegram.ext import Application

StartTime = time.time()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)


from MainBot.sample_config import Development as Config

TOKEN = Config.TOKEN
OWNER_USERNAME = Config.OWNER_USERNAME
OWNER_ID = Config.OWNER_ID
ADMINS = Config.ADMINS
ADMINS.add(OWNER_ID)
application = Application.builder().token(TOKEN).build()
ERROR_LOGS = Config.ERROR_LOGS
DB_URI = Config.SQLALCHEMY_DATABASE_URI
BOT_USERNAME = Config.BOT_USERNAME
FIRST_NAMES = Config.FIRST_NAMES
CURRENT_USERS = Config.CURRENT_USERS
EVENT_LOGS = Config.EVENT_LOGS
MAIN_CHANNEL = Config.MAIN_CHANNEL
FORCE_SUB = Config.FORCE_SUB
BATCH_FILES = Config.BATCH_FILES
PROTECT_CONTENT = Config.PROTECT_CONTENT
