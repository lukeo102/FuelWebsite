import datetime
from json import dumps
from secrets import token_urlsafe
from flask import request, session, redirect, url_for
from pymongo import cursor
from .utils import render_login_register, format_date
from ..log import Log
from ..database import Database
from bcrypt import gensalt, hashpw
from validate_email import validate_email
from .verify import generate_code, send_code


def validate_token(token, username, db: Database):
    db_user = db.find_one("token", {'username': username, 'token': token})

    if db_user is None:
        return False

    if not format_date(datetime.datetime.now()) < db_user.get('expiry'):
        db.remove('token', {'username': username, 'token': token})
        return False

    return True


def validate_login(username, password, db: Database):
    db_user = db.find_one('users', {'username': username})
    if db_user is None:
        return False

    hashed_pass = hash_pass(password, db_user.get('salt'))
    if hashed_pass[0] == db_user.get('password'):
        return True

    return False


def hash_pass(password, salt=None):
    if salt is None:
        salt = gensalt()

    hashed = hashpw(password.encode('utf-8'), salt)
    return [hashed, salt]


def generate_token(username, db: Database):
    unique = False
    token = None
    while not unique:
        token = token_urlsafe(64)
        db_result = db.find_one('token', {'token': token})
        if db_result is None:
            unique = True

    if token is None:
        return False

    expiry = datetime.datetime.now() + datetime.timedelta(days=30)
    expiry = format_date(expiry)
    db.insert('token', {
        'username': username,
        'token': token,
        'expiry': expiry
    })

    return token


def get_request_data(register=False, db: Database = None):
    details = {}
    try:
        details['username'] = request.values['username']
        details['password'] = request.values['password']
        if register:
            details['confirm-password'] = request.values['confirm-password']
            details['email'] = request.values['email']
        else:
            if db is None:
                raise KeyError

    except KeyError as e:
        return None

    return details


def login_page(db: Database, log=Log(Id="Login", init_msg=False)):
    # try:
    session.clear()

    if request.method == "POST":
        try:
            button = request.form['submit']
        except KeyError as e:
            return render_login_register()

        if button == "Login":
            return login(db)

        elif button == 'Register':
            return register(db)

    return render_login_register()


# except Exception as error:
#     return render_login_register(error=True)


def register(db: Database):
    # Check email and username have not been used, check email is valid (send code?), check password isnt null, register user, stuff
    details = request.form
    if details is None:
        return render_login_register(error=True)

    error = False
    status = {
        'invalid_username': False,
        'username_taken': False,
        'invalid_email': False,
        'email_registered': False,
        'invalid_password': False,
        'password_dont_match': False
    }

    # Input validation, 0 < username < 21, email exists, password exists and matches confirm password
    # Username
    if not 1 <= len(details['username']) <= 20:
        status['invalid_username'] = True
        error = True

    # Email
    v = validate_email(details['email'])

    if v is not True:
        status['invalid_email'] = True
        error = True

    # Password
    if not 1 <= len(details['password']) <= 60:
        status['invalid_password'] = True
        error = True

    if not details['password'] == details['confirm-password']:
        status['password_dont_match'] = True
        error = True

    # Check username and email dont already exist
    user_check: cursor.Cursor = db.find_one("users", {"username": details['username']})
    email_check: cursor.Cursor = db.find_one("users", {"email": details['email']})

    # Username
    if user_check is not None:
        status['username_taken'] = True
        error = True

    # Email
    if email_check is not None:
        status['email_registered'] = True
        error = True

    # If errors, dont register, get new input
    if error:
        return render_login_register(register=status)

    else:
        # Register user
        hashed, salt = hash_pass(details['password'])
        data = {
            'username': details['username'],
            'password': hashed,
            'email': details['email'],
            'salt': salt,
            'units': details['units'],
            'distance': details['distance'],
            'currency': details['currency'],
            'odometer': details['distance'],
            'verified': False
        }

        db.insert('users', data)

        verify_code = generate_code(details['username'])

        data = {
            'username': details['username'],
            'email': details['email'],
            'code': verify_code
        }

        db.insert('verify', data)

        send_code(
            generate_code(details['username']),
            details['email'],
            details['username']
        )

        return redirect(url_for('verify_route', register=True))


def login(db: Database):
    details = get_request_data(db=db)
    if details is None:
        return render_login_register(error=True)

    db_user = db.find_one("users", {"username": details['username']})
    if db_user is None:
        return render_login_register(login=True)

    if not validate_login(details['username'], details['password'], db):
        return render_login_register(login=True)

    token = generate_token(details['username'], db)
    session['token'] = token
    session['username'] = details['username']

    return redirect(url_for('default_route'))
