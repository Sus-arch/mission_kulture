from flask import Flask, render_template, make_response, jsonify, redirect
import flask_login
from flask_login import LoginManager, login_user, logout_user, login_required
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from forms.object import AddObject
from data.objects import Object
from waitress import serve
import os
import json
from random import randint


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
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.nick == form.nick.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким ником уже зарегистрирован")
        user = User(
            email=form.email.data,
            nick=form.nick.data,
            is_admin=0
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_object', methods=['GET', 'POST'])
def add_object():
    if not flask_login.current_user.is_authenticated or not flask_login.current_user.is_admin:
        return jsonify({'error': 'access denied'})
    form = AddObject()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Object).filter(Object.reester_number == form.reester_number.data).first():
            return render_template('add_object.html', form=form, message='Объект с таким номером уже зарегистрирован')
        obj = Object(
            name=form.name.data,
            about=form.about.data,
            reester_number=form.reester_number.data,
            region=form.region.data,
            full_address=form.full_address.data,
            category=form.category.data,
            kind=form.kind.data,
            unesco=form.unesco.data,
            is_value=form.is_value.data,
            coords=form.coords.data
        )
        db_sess.add(obj)
        db_sess.commit()
        return redirect('/')

    return render_template('add_object.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/show')
def show_objects():
    db_sess = db_session.create_session()
    objects = db_sess.query(Object).all()
    obj = [objects[randint(1, len(objects))] for _ in range(10)]
    return render_template('show_objects.html', obj=obj)


@app.route('/object/<int:object_id>', methods=['GET', 'POST'])
def get_object(object_id):
    db_sess = db_session.create_session()
    obj = db_sess.query(Object).get(object_id)
    if obj:
        return render_template('object.html', obj=obj)
    return jsonify({'error': 'object not found'})


def add_all_objects():
    db_sess = db_session.create_session()
    os.chdir('obj')
    l = os.listdir()
    for i in l:
        with open(i, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for j in data:
                name = j['nativeName']
                region = j['data']['general']['region']['value']
                reester_number = j['data']['general']['regNumber']
                category = j['data']['general']['categoryType']['value']
                kind = j['data']['general']['objectType']['value']
                about = j['data']['general']['name']
                try:
                    unesco = j['data']['general']['unesco']['value']
                except:
                    unesco = 0
                try:
                    is_value = j['data']['general']['status']['value']
                except:
                    is_value = 0
                try:
                    full_address = j['data']['general']['address']['fullAddress']
                except:
                    full_address = ''
                try:
                    coords = j['data']['general']['address']['mapPosition']['coordinates']
                except:
                    coords = ''
                try:
                    photo = j['data']['general']['photo']['url']
                except:
                    photo = ''
                if unesco == 'нет':
                    unesco = 0
                elif unesco == 'да':
                    unesco = 1
                if is_value == 'нет':
                    is_value = 0
                elif is_value == 'да':
                    is_value = 1

                obj = Object(name=name,
                             region=region,
                             reester_number=reester_number,
                             category=category,
                             kind=kind,
                             about=about,
                             unesco=unesco,
                             is_value=is_value,
                             full_address=full_address,
                             coords=str(coords),
                             photo=photo)
                db_sess.add(obj)
                db_sess.commit()


def main():
    db_session.global_init('db/culture.db')
    port = int(os.environ.get("PORT", 5000))
    app.run(port=5000, host='0.0.0.0')
    # serve(app, port=port, host='0.0.0.0')
    # add_all_objects()


if __name__ == '__main__':
    main()