class Config(object):
    TOKEN = "BOT_TOKEN_HERE"  # bot token from bot father
    BOT_USERNAME = "BOT_USERNAME_HERE"  # bot username
    OWNER_ID = "OWNER_ID_HERE"  # Owner account user id
    OWNER_USERNAME = "OWNER_USERNAME_HERE"  # Owner account username
    API_ID = 12345  # account api id from telegram website
    API_HASH = "API_HASH HERE"  # account api hash from telegram website
    SQLALCHEMY_DATABASE_URI = "MONGODB_DATABASE_URI"  # format : mongodb+srv://account:password@db.2tlwppk.mongodb.net/mainbot?retryWrites=true&w=majority
    ADMINS = set(["1608141072"])
    ERROR_LOGS = -100111111111  # error logging group id here
    FIRST_NAMES = {}
    CURRENT_USERS = set([])
    EVENT_LOGS = -100111111111  # new joinee logger id
    MAIN_CHANNEL = -100111111111  # database channel id
    FORCE_SUB = {"id": "-1002075202906"}  # force sub channel default id
    BATCH_FILES = {"status": False}


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
