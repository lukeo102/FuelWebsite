from flask import request, render_template, session
from pymongo.database import Database
from .utils import render_head, render_header, render_footer


def default(db: Database):
    return ""


def main(db: Database):
    page = render_head(title="Previous Fill Ups") \
        + render_header(username=session['username']) \
        + render_template('history/default_header.jinja2')

    if request.method == 'get':
        section = request.values['section']

    else:
        section = default

    match section:
        case _:
            page += default(db)

    return page