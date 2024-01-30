import http

from flask import request, render_template, session, jsonify
from ..database import Database
from .utils import render_head, render_header
from ..log import Log

def main(db: Database):
    page = render_head(title="Previous Fill Ups", javascript=["history.css"]) \
           + render_header(username=session['username']) \
           + render_template('history/history_header.jinja2')

    if request.method == 'post':
        if session['username'] is None:
            return "ERROR 401 Unauthorised"

        section = request.values['section']

    return page


def section_handler(db: Database, section, log: Log = None):
    match section:
        case "efficiency":
            return efficiency_section(db)

        case "all":
            return jsonify(all_section(db))

        case "delete_fill_up":
            return delete_fill_up(db)

        case _:
            return http.HTTPStatus.BAD_REQUEST


def delete_fill_up(db: Database):
    data = request.args
    try:
        id = data['_id']

    except KeyError:
        return http.HTTPStatus.BAD_REQUEST

    try:
        if db.remove("fill_ups", {"_id": id, "username": session['username']}).deleted_count > 0:
            return http.HTTPStatus.OK

        else:
            return http.HTTPStatus.FORBIDDEN


    except Exception as e:
        return http.HTTPStatus.BAD_REQUEST



def all_section(db: Database):
    try:
        details = {}

        for vehicle in db.find("vehicles", {"username": session['username']}, {"_id": 0, "username": 0}):
            details[vehicle['nickname']] = []
            for i, record in enumerate(db.find("fill_ups", {"username": session['username'], "vehicle": vehicle['nickname']}, {
                "vehicle": 0,
                "username": 0
            })):
                details[vehicle['nickname']].append({})
                for key, value in record.items():
                    if key == "_id":
                        details[vehicle['nickname']][i][key] = str(value)
                    else:
                        details[vehicle['nickname']][i][key] = value

        print(details)
        return [details]

    except Exception as e:
        print(e)
        return http.HTTPStatus.IM_A_TEAPOT

def efficiency_section(db: Database):
    user = session['username']

