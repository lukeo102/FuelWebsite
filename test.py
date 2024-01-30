
from src.database import Database

db = Database()
for item in db.find("fill_ups", {"username": "luke", "vehicle": "CB650F"}):
    print(item)


print("done")
exit(2)