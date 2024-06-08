class Config(object):
    pass


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
