import http

from flask import request, render_template, session
from pymongo.database import Database
from utils import render_head, render_header, render_footer
import history


def main(db: Database):
    page = render_head(title="Previous Fill Ups") \
           + render_header(username=session['username']) \
           + render_template('history/history_header.jinja2')

    if request.method == 'post':
        if session['username'] is None:
            return "ERROR 401 Unauthorised"

        section = request.values['section']

        match section:
            case "efficiency":
                return get_efficiency(db, session['username'])

    return page


def section_handler(db: Database, section):
    match section:
        case "efficiency":
            return

        case _:
            return http.HTTPStatus.BAD_REQUEST
