from flask import Flask, session, redirect, url_for, request
from src.pages import login, test, about, previous_fill_up, record_fill_up, settings, verify
from .login import validate_token
from ..log import Log
from ..database import Database


class Manager:
    def __init__(self, port=8080, log=Log(Id="Manager", init_msg=False)):
        self.app = Flask(__name__, template_folder='../../templates', static_folder='../../static')
        self.log = log
        self.port = port
        self.db = Database()
        self.session_secret = self.db.get_session_secret()
        self.app.secret_key = self.session_secret

    def run(self):
        app = self.app
        log = self.log

        def loggedin_handle(page, section=None):
            try:
                valid_token = validate_token(session['token'], session['username'], self.db)

            except KeyError as e:
                valid_token = False

            if not valid_token:
                session.clear()
                return redirect(url_for("login_route"))

            match page:
                case "fill_up":
                    return record_fill_up.main(db=self.db)

                case "prev_fill_up":
                    return previous_fill_up.main(db=self.db)

                case "settings":
                    return settings.main(db=self.db)

                case "remove_vehicle":
                    return settings.remove_vehicle(db=self.db)

                case "add_vehicle":
                    return settings.add_vehicle(db=self.db)

                case "query":
                    return previous_fill_up.section_handler(self.db, section)


        @app.route('/test', methods=['GET', 'POST'])
        def test_route():
            return test.test_page()

        @app.route('/login', methods=['GET', 'POST'])
        def login_route():
            return login.login_page(db=self.db)

        @app.route('/verify', methods=['GET', 'POST'])
        def verify_route():
            return verify.main(self.db)

        @app.route('/about', methods=['GET', 'POST'])
        def about_route():
            return about.about(db=self.db)

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
                    more = self.db.remove("token", {"username": session['username']}).deleted_count

            else:
                try:
                    self.db.remove('token', {'token': session['token']})
                except KeyError as e:
                    pass

            session.clear()
            return redirect(url_for("login_route"))

        self.app.run(host="0.0.0.0", port=self.port, debug=True)
