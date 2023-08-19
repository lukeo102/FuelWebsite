import datetime
from flask import url_for, render_template
from typing import List


def render_login_register(login: bool = False, register=None, error: bool = False):
    """
    :param login: invalid username or password
    :param register: [username taken, username too long, invalid email, successful register]
    :return: html ready to be sent to client
    """
    if register is None:
        register = {
            'invalid_username': False,
            'username_taken': False,
            'invalid_email': False,
            'email_registered': False,
            'invalid_password': False,
            'password_dont_match': False,
            'register_success': False
        }

    return render_head("Login", ["login.css"]) \
           + render_template("loginRegister.jinja2", login=login, register=register, error=error) \
           + render_footer()


def format_date(date: datetime.datetime):
    return int(date.strftime('%Y%m%d%H%M%S'))


def render_head(title, stylesheets: List[str] = [], javascript: List[str] = []):
    formatted_css = [
        url_for('static', filename=f'css/default.css'),
        url_for('static', filename=f'css/header.css'),
        url_for('static', filename=f'css/footer.css'),
    ]

    formatted_js = []

    for sheet in stylesheets:
        formatted_css.append(url_for('static', filename=f'css/{sheet}'))

    for script in javascript:
        formatted_js.append(url_for('static', filename=f'javascript/{script}'))

    return render_template("head.jinja2", title=title, stylesheets=formatted_css, javascript=formatted_js)


def render_header(username):
    return render_template("header.jinja2", username=username)


def render_footer():
    return render_template("footer.jinja2")

