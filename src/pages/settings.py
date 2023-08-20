import http

from flask import request, render_template, session
from src.database import Database
from src.pages.utils import render_footer, render_head, render_header


def return_page(saved, currency='?', units='?', distance='?', odometer='?', vehicle_list=None, vehicle_exists=False, vehicle_added=False, vehicle_removed=False):
    if vehicle_list is None:
        vehicle_list = []

    return render_head("Settings", ["settings.css"]) \
           + render_header(username=session['username']) \
           + render_template(
            "settings.jinja2",
            submit=saved,
            currency=currency,
            units=units,
            distance=distance,
            odometer=odometer,
            vehicle_list=vehicle_list,
            vehicle_exists=vehicle_exists,
            vehicle_added=vehicle_added,
            vehicle_removed=vehicle_removed
        ) \
           + render_footer()


def main(db: Database, vehicle_exists=False, vehicle_added=False, vehicle_removed=False):
    saved = False
    db_user = db.find_one('users', {'username': session['username']})

    # Read pre-exisiting user preferences
    try:
        currency = db_user.get('currency')
        units = db_user.get('units')
        distance = db_user.get('distance')
        odometer = db_user.get('odometer')
    except Exception as e:
        return http.HTTPStatus.BAD_REQUEST

    # Get list of users' vehicles
    vehicle_list = get_vehicle_list(session['username'], db)

    # Get updated user preferences
    if request.method == 'POST' and not vehicle_exists and not vehicle_added and not vehicle_removed:
        try:
            units = request.values['units']
            currency = request.values['currency']
            distance = request.values['distance']
            odometer = request.values['odometer']
            saved = True

        except KeyError as e:
            return return_page(False)

        db.update('users', {'username': session['username']}, {
            'currency': f'{currency}',
            'units': units,
            'distance': distance,
            'odometer': odometer
        })

    return return_page(saved, currency, units, distance, odometer, vehicle_list, vehicle_exists, vehicle_added, vehicle_removed)

def add_vehicle(db: Database):
    # Check vehicle doesnt exist already
    # Add vehicle to database
    # refresh page
    try:
        vehicle = request.values["new-vehicle"]

    except Exception as e:
        return http.HTTPStatus.BAD_REQUEST

    # Check vehicle doesnt already exist
    if db.find_one("vehicles", {"username": session['username'], "nickname": vehicle}) is not None:
        return main(db, vehicle_exists=True)

    # Add vehicle to database
    else:
        db.insert("vehicles", {"username": session['username'], "nickname": vehicle})
        return main(db, vehicle_added=True)



def remove_vehicle(db: Database):
    # check valid request
    # remove all fill ups
    # remove vehicle
    try:
        vehicle = request.values['nickname']

    except Exception as e:
        return http.HTTPStatus.BAD_REQUEST

    more = 1
    while more:
        more = db.remove("fill_ups", {"username": session['username'], "vehicle": vehicle}).deleted_count

    db.remove("vehicles", {"username": session['username'], "nickname": vehicle})

    return main(db, vehicle_removed=True)
    # remove all references to the users' vehicle

def get_vehicle_list(user, db: Database):
    vehicle_list = []
    for vehicle in db.find("vehicles", {"username": session['username']}):
        vehicle_list.append(vehicle.get("nickname"))

    return vehicle_list