import smtplib
from flask import request, url_for, redirect, render_template
from base64 import b64encode
from src.database import Database
from os import urandom
from hashlib import md5
from ..constants import WEBSITE_URL
from .utils import render_head


def verify_code(code, db: Database):
    db_result = db.find_one('verify', {'code': code})
    if db_result is None:
        return default_page(verify_error=True)

    email = db_result.get('email')
    db.remove('verify', {'code': code})
    db.update('users', {'email': email}, {'verified': True})
    return default_page(register=True)


def default_page(error=False, register=False, verify_error=False):
    page = render_head(title="Verify") + render_template(
        'verify.jinja2',
        error=error,
        register=register,
        verify_error=verify_error
    )
    return page


def generate_code(username):
    random_num = str(urandom(32))
    hash = md5(b64encode(username + random_num))
    return hash


def send_code(code, email, username):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()

    try:
        server.login("lofuelwebs@gmail.com", "gzvokkxfnfgjiito")
    except smtplib.SMTPAuthenticationError as e:
        print(e)
        return

    url = WEBSITE_URL + url_for('verify_route', code=code)

    email_text = f"""\
    From: lofuelwebs@gmail.com
    To: {email}
    Subject: Verify your email

    Welcome {username},
    
    Please click the link below to verify your email.
    {url}
    """

    server.sendmail("lofuelwebs@gmail.com", "lukeormiston@gmail.com", email_text)
    server.close()
    server.quit()


def main(db: Database):
    if request.method == 'GET':
        key = request.values.keys()
        if not len(key) == 1:  # Should only ever get one value in the get request
            print(len(key))
            return default_page(error=True)

        for k in key:
            match k:
                case "register":
                    return default_page(register=True)

                case "code":
                    return verify_code(code=request.values['code'], db=db)

                case _:
                    print(k)
                    return default_page(error=True)

    return default_page()
