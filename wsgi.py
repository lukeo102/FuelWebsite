from flask import Flask, session, redirect, url_for, request
from src.pages import login, test, about, previous_fill_up, record_fill_up, settings, verify
from src.pages.login import validate_token
from src.log import Log
from src.database import Database
import os

cwd = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=f'{cwd}/templates', static_folder=f'{cwd}/static')
log = Log(Id="Manager", init_msg=False)
port = 8080
db = Database()
session_secret = db.get_session_secret()
app.secret_key = session_secret

log.append_log(f"Current working directory: {cwd}")


def loggedin_handle(page, section=None):
    try:
        valid_token = validate_token(session['token'], session['username'], db)

    except KeyError as e:
        valid_token = False

    if not valid_token:
        session.clear()
        return redirect(url_for("login_route"))

    match page:
        case "fill_up":
            return record_fill_up.main(db=Database())

        case "prev_fill_up":
            return previous_fill_up.main(db=Database())

        case "settings":
            return settings.main(db=Database())

        case "remove_vehicle":
            return settings.remove_vehicle(db=Database())

        case "add_vehicle":
            return settings.add_vehicle(db=Database())

        case "query":
            return previous_fill_up.section_handler(Database(), section)


@app.route('/test', methods=['GET', 'POST'])
def test_route():
    return test.test_page()

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    return login.login_page(db=Database())

@app.route('/verify', methods=['GET', 'POST'])
def verify_route():
    return verify.main(Database())

@app.route('/about', methods=['GET', 'POST'])
def about_route():
    return about.about(db=Database())

@app.route('/', methods=['GET', 'POST'])
def default_route():
    return loggedin_handle("fill_up")

@app.route('/history', methods=['GET', 'POST'])
@app.route('/history/<string:sub>', methods=['GET', 'POST'])
def prev_fill_up_route(sub=None):
    if sub is not None:
        return loggedin_handle("query", sub)

    return loggedin_handle("prev_fill_up")

@app.route('/settings', methods=['GET', 'POST'])
@app.route('/settings/<string:sub>', methods=['GET', 'POST'])
def settings_route(sub=None):
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
    if request.path == "/logout/all":
        more = 1
        while more:
            more = db.remove("token", {"username": session['username']}).deleted_count

    else:
        try:
            db.remove('token', {'token': session['token']})
        except KeyError as e:
            pass

    session.clear()
    return redirect(url_for("login_route"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
