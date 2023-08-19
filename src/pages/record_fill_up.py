import datetime

from flask import request, session, render_template, redirect, url_for
from src.database import Database
from src.pages.utils import render_head, render_header

def process_new_fillup(amount, cost, currency, units, db: Database):
    now = datetime.datetime.now()
    db.insert('fill_ups', {
        'username': session['username'],
        'amount': amount,
        'cost': cost,
        'date': now,
        'currency': currency,
        'units': units
    })


def main(db: Database):
    try:
        amount = request.values['amount']
        cost = request.values['cost']

    except KeyError as e:
        amount = None
        cost = None

        try:
            processed = request.values['submitted']

        except KeyError as e:
            processed = None

    user_db = db.find_one('users', {'username': session['username']})
    units = user_db.get('units')
    currency = user_db.get('currency')

    if amount is not None and cost is not None:
        process_new_fillup(amount, cost, currency, units, db)
        return redirect(url_for('default_route') + "?submitted=True")

    print()
    return render_head("Home") \
        + render_header(session['username']) \
        + render_template('recordFillUpForm.jinja2', processed=processed, units=units, currency=currency)


