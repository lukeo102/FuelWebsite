from flask import request, render_template, session
from src.database import Database
from src.pages.utils import render_footer, render_head, render_header


def return_page(saved, currency='?', units='?', distance='?', odometer='?'):
    return render_head("Settings", ["settings.css"]) \
           + render_header(username=session['username']) \
           + render_template("settings.jinja2", submit=saved, currency=currency, units=units, distance=distance, odometer=odometer) \
           + render_footer()


def main(db: Database):
    saved = False
    db_user = db.find_one('users', {'username': session['username']})

    # Read pre-exisiting user preferences
    try:
        currency = db_user.get('currency')
        units = db_user.get('units')
        distance = db_user.get('distance')
        odometer = db_user.get('odometer')
    except Exception as e:
        return '<p>Unexpected error</p>'

    # Get updated user preferences
    if request.method == 'POST':
        try:
            units = request.values['units']
            currency = request.values['currency']
            distance = request.values['distance']
            odometer = request.values['odometer']
            saved = True

        except KeyError as e:
            return return_page(False)

        db.update('users', {'username': session['username']}, {'currency': f'{currency}', 'units': units, 'distance': distance, 'odometer': odometer})

    return return_page(saved, currency, units, distance, odometer)
