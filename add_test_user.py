from src.database import Database
from datetime import datetime, timedelta
from src.pages.login import hash_pass
from random import randint, seed

# Changeable variables
username = "test"
vehicle_names = ["bike", "car"]
average_mpg = [60, 45]
fuel_capacity = [15, 55]
cost_per_litre = 1.5
date_range = ["23/01/2002", "23/01/2024"]
average_fill_up_frequency_days = 10  # Min 5


# Static variables
seed(datetime.utcnow().microsecond)
liter_to_gallon_division = 4.546
datetime_generator = lambda date: datetime.strptime(date, "%d/%m/%Y")
fill_ups = {name: [] for name in vehicle_names}
curr_date = datetime_generator(date_range[0])
last_capacity = [0 for item in vehicle_names]
last_cost = [0 for _ in vehicle_names]
odometer = [0 for _ in vehicle_names]
date = [datetime_generator(date_range[0]) for _ in vehicle_names]

# Generate fill ups
while date[0] < datetime_generator(date_range[1]):
    # Add a variance of 10 days between fill ups
    refill_delta = timedelta(days=average_fill_up_frequency_days + randint(-5, 5))
    for i, name in enumerate(vehicle_names):
        # Use between 20% and 60% of tank
        use_amount = fuel_capacity[i] * (randint(2, 6) / 10)
        # Add fuel usage to odometer between 70% and 130% of the average mpg (60% variance)
        odometer[i] += use_amount * ((average_mpg[i] * (randint(70, 130) / 100)) / liter_to_gallon_division)
        if i == 0:
            print(odometer[i], use_amount)
        # Refill to full
        fill_amount = fuel_capacity[i] - use_amount
        fill_cost = fill_amount * cost_per_litre
        date[i] = date[i] + refill_delta

        fill_ups[name].append({
            'username': username,
            'amount': fill_amount,
            'cost': fill_cost,
            'odometer': int(odometer[i]),
            'odometer_units': "Miles",
            'date': date[i],
            'currency': "£",
            'units': "Litre",
            'vehicle': vehicle_names[i]
        })

db = Database()
if db.find_one("users", {'username': username}) is not None:
    print("user already exists, deleting")
    while db.remove("fill_ups", {'username': username}).deleted_count:
        pass
    while db.remove("vehicles", {'username': username}).deleted_count:
        pass
    while db.remove("token", {'username': username}).deleted_count:
        pass
    while db.remove("users", {'username': username}).deleted_count:
        pass

password, salt = hash_pass(username)
db.insert("users", {
    'username': username,
    'password': password,
    'salt': salt,
    'units': "Litre",
    'distance': "Miles",
    'currency': "£",
    'odometer': "Miles",
})

for vehicle in vehicle_names:
    db.insert("vehicles", {"username": username, "nickname": vehicle})
    for fill_up in fill_ups[vehicle]:
        db.insert('fill_ups', fill_up)
