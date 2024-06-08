from MainBot import DB_URI
import pymongo

client = pymongo.MongoClient(DB_URI)
db = client.mainbot
