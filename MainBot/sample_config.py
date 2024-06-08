class Config(object):
    TOKEN = (
        "7176615214:AAH57jHjXiEM8XNUzkYWpTnVhhUxJuWxtDY"  # bot token from bot father
    )
    BOT_USERNAME = "dhffhiofodsbot"  # bot username
    OWNER_ID = "1608141072"  # Owner account user id
    OWNER_USERNAME = "goyalcompany"  # Owner account username
    SQLALCHEMY_DATABASE_URI = "mongodb+srv://internshala:internshala@internshala.2tlwppk.mongodb.net/mainbot?retryWrites=true&w=majority"  # format : mongodb+srv://account:password@db.2tlwppk.mongodb.net/mainbot?retryWrites=true&w=majority
    ADMINS = set(["1608141072"])
    ERROR_LOGS = -1002238572635  # error logging group id here
    FIRST_NAMES = {}
    CURRENT_USERS = set([])
    EVENT_LOGS = -1002238572635  # new joinee logger id
    MAIN_CHANNEL = -1002238572635  # database channel id
    FORCE_SUB = {"id": "-1002238572635"}  # force sub channel default id
    BATCH_FILES = {"status": False}
    PROTECT_CONTENT = True


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
