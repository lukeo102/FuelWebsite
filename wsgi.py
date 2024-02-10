import os

from flask import Flask, session, redirect, url_for, request
from werkzeug.exceptions import HTTPException

from src.pages import login, test, about, previous_fill_up, record_fill_up, settings, verify
from src.pages.login import validate_token
from src.log import Log
from src.database import Database
from src.constants import CWD

app = Flask(__name__, template_folder=f'{CWD}/templates', static_folder=f'{CWD}/static')
log = Log(Id="Manager", init_msg=False)
port = 8080
app.secret_key = Database().get_session_secret()

log.append_log(f"Current working directory: {CWD}")


def loggedin_handle(page, section=None):
    db = Database()
    try:
        valid_token = validate_token(session['token'], session['username'], db)

    except KeyError as e:
        valid_token = False

    if not valid_token:
        session.clear()
        return redirect(url_for("login_route"))

    match page:
        case "fill_up":
            return record_fill_up.main(db=db)

        case "prev_fill_up":
            return previous_fill_up.main(db=db)

        case "settings":
            return settings.main(db=db)

        case "remove_vehicle":
            return settings.remove_vehicle(db=db)

        case "add_vehicle":
            return settings.add_vehicle(db=db)

        case "query":
            return previous_fill_up.section_handler(db, section)


@app.route('/test', methods=['GET', 'POST'])
def test_route():
    return test.test_page()


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    log.append_log("Login route")
    return login.login_page(db=Database())


@app.route('/verify', methods=['GET', 'POST'])
def verify_route():
    log.append_log("Verify route")
    return verify.main(Database())


@app.route('/about', methods=['GET', 'POST'])
def about_route():
    log.append_log("About route")
    return about.about(db=Database())


@app.route('/', methods=['GET', 'POST'])
def default_route():
    log.append_log("Default route")
    return loggedin_handle("fill_up")


@app.route('/history', methods=['GET', 'POST'])
@app.route('/history/<string:sub>', methods=['GET', 'POST'])
def prev_fill_up_route(sub=None):
    log.append_log("")
    if sub is not None:
        return loggedin_handle("query", sub)

    return loggedin_handle("prev_fill_up")


@app.route('/settings', methods=['GET', 'POST'])
@app.route('/settings/<string:sub>', methods=['GET', 'POST'])
def settings_route(sub=None):
    log.append_log("Settings route")
    match sub:
        case "add_vehicle":
            return loggedin_handle("add_vehicle")
        case "remove_vehicle":
            return loggedin_handle("remove_vehicle")
        case _:
            return loggedin_handle("settings")


@app.route('/logout', methods=['GET', 'POST'])
@app.route('/logout/all', methods=['GET', 'POST'])
def logout_route():
    log.append_log("Logout Route")
    db = Database()
    try:
        if request.path == "/logout/all":
            log.append_log("Logout all")
            more = 1
            while more:
                more = db.remove("token", {"username": session['username']}).deleted_count

        else:
            db.remove('token', {'token': session['token']})

    except KeyError as e:
        raise HTTPException

    session.clear()
    return redirect(url_for("login_route"))


@app.errorhandler(HTTPException)
def handle_bad_request():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
