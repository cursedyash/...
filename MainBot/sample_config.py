class Config(object):
        TOKEN = (
        ""  # bot token from bot >
    )
    BOT_USERNAME = ""  # bot username
    OWNER_ID = ""  # Owner account user id
    OWNER_USERNAME = ""  # Owner account username
    SQLALCHEMY_DATABASE_URI = ""
    ADMINS = set(["1439206175"])
    ERROR_LOGS = -1002096520973  # error logging group id here
    FIRST_NAMES = {}
    CURRENT_USERS = set([])
    EVENT_LOGS = -1002096520973  # new joinee logger id
    MAIN_CHANNEL = -1002109329180  # database channel id
    FORCE_SUB = {"id": ""}  # force sub channel default id
    BATCH_FILES = {"status": False}
    PROTECT_CONTENT = True




class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
