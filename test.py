
from src.database import Database
from bson.objectid import ObjectId
db = Database()
id = ObjectId('65b41cc83d8ea0323f8529b1')
print(db.find_one("fill_ups", {"_id": id, "username": "luke"}))