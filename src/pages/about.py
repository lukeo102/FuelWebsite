from flask import session, render_template, request

from .login import validate_token
from .utils import render_header, render_head, render_footer
from ..database import Database


def about(db: Database):
    page = render_head(title="About", stylesheets=["about.css"])

    try:
        loggedin = validate_token(session['token'], session['username'], db)
        if loggedin:
            page += render_header(username=session['username'])


    except KeyError as e:
        loggedin = False

    try:
        if validate_token(session['token']):
            page += render_header(session['username'])

    except Exception as e:
        pass

    previous_page = request.referrer

    page += render_template('about.jinja2', previous_page=previous_page, loggedin=loggedin)
    page += render_footer()
    return page
