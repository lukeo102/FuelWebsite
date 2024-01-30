import traceback

import pymongo
from pymongo.errors import ServerSelectionTimeoutError
from secrets import token_hex
from .log import Log


class Database:
    def __init__(self, address="localhost", port=27017, log=Log(Id="Database")):
        self.log = log
        try:
            self.conn = pymongo.MongoClient(f"mongodb://{address}:{port}")
            self.db = self.conn.get_database("fuel")

            secret = self.find('config', {"session_secret": {'$exists': True}}, {'session_secret': 1})
            self.session_secret = secret.next()['session_secret']

        except ServerSelectionTimeoutError as e:
            log.append_log("Failed to establish connection to database server", 4)
            exit(2)

        except StopIteration as e:
            self.log.append_log("Session secret was not found, generating and storing new one", 3)
            secret = token_hex(32)
            self.insert("config", {"session_secret": secret})
            self.session_secret = secret

    def insert(self, collection: str, data: dict):
        coll = self.db.get_collection(collection)
        return coll.insert_one(data)

    def remove(self, collection: str, data: dict):
        coll = self.db.get_collection(collection)
        return coll.delete_one(data)

    def find_one(self, collection: str, data: dict):
        coll = self.db.get_collection(collection)
        return coll.find_one(data)

    def find(self, collection: str, data: dict, kwargs: dict = dict()):
        coll = self.db.get_collection(collection)
        return coll.find(data, kwargs)

    def update(self, collection: str, data: dict, updated_data: dict):
        coll = self.db.get_collection(collection)
        return coll.update_one(data, {'$set': updated_data})

    def get_session_secret(self):
        return self.session_secret

    def __del__(self):
        self.conn.close()
