from flask import Flask, render_template, make_response, jsonify, redirect
import flask_login
from flask_login import LoginManager, login_user, logout_user, login_required
from data import db_session
from data.users import User
from data.objects import Object
from waitress import serve
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'NJwadok12LMKF3KMlmcd232v_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    pass


def main():
    db_session.global_init('db/culture.db')
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
    # serve(app, port=port, host='0.0.0.0')


if __name__ == '__main__':
    main()