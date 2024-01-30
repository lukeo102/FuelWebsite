
from src.database import Database

db = Database()
for item in db.find("users", {}):
    print(item)


print("done")
exit(2)