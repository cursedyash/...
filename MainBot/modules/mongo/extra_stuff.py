import threading
from MainBot.modules.mongo import db
from MainBot import FORCE_SUB

USERS_COLLECTION = db["extra_stuff"]
INSERTION_LOCK = threading.RLock()


def get_all_higher_users():
    ret = set([])
    admins = USERS_COLLECTION.find_one({"name": "admins"})
    if admins:
        for el in admins["users"]:
            ret.add(el)
    return ret


def add_admin(user_id):
    with INSERTION_LOCK:
        curr = USERS_COLLECTION.find_one({"name": "admins"})
        if curr:
            curr["users"][user_id] = True
            USERS_COLLECTION.update_one({"name": "admins"}, {"$set": curr})
            return True
        else:
            document = {"name": "admins", "users": {user_id: True}}
            USERS_COLLECTION.insert_one(document)
            return True


def remove_admin(user_id):
    with INSERTION_LOCK:
        curr = USERS_COLLECTION.find_one({"name": "admins"})
        if curr:
            if user_id in curr["users"]:
                del curr["users"][user_id]
                USERS_COLLECTION.update_one({"name": "admins"}, {"$set": curr})
                return True
        return False


def add_force_sub(id):
    with INSERTION_LOCK:
        curr = USERS_COLLECTION.find_one({"name": "forcesub"})
        if curr:
            curr["id"] = id
            USERS_COLLECTION.update_one({"name": "forcesub"}, {"$set": curr})
        else:
            document = {"name": "forcesub", "id": id}
            USERS_COLLECTION.insert_one(document)
        FORCE_SUB["id"] = id
        return True


def remove_force_sub():
    with INSERTION_LOCK:
        curr = USERS_COLLECTION.find_one({"name": "forcesub"})
        if curr:
            curr["id"] = ""
            USERS_COLLECTION.update_one({"name": "forcesub"}, {"$set": curr})
        else:
            document = {"name": "forcesub", "id": ""}
            USERS_COLLECTION.insert_one(document)
        FORCE_SUB["id"] = ""
        return True


def get_force_sub():
    return USERS_COLLECTION.find_one({"name": "forcesub"})
