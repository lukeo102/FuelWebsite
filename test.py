
from src.database import Database

db = Database()
more = 1
while more:
    print("DELETING")
    more = db.remove("fill_ups", {"username": "Luke", "vehicle": "test2"}).deleted_count
