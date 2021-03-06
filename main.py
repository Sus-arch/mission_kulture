from flask import Flask, render_template, make_response, jsonify, redirect, request, url_for, session
import flask_login
from flask_login import LoginManager, login_user, logout_user, login_required
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from forms.object import AddObject, FindObjectForm
from data.objects import Object
from data.comments import Comment
from data.category import Category
from data.region import Region
from data.kind import Kind
from forms.comment import AddCommentForm
from waitress import serve
import os
import json
from random import randint
import sys
import requests
from PIL import Image
import urllib3
from utils.file_reader import get_text
from flask_caching import Cache


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
app.config['SECRET_KEY'] = 'NJwadok12LMKF3KMlmcd232v_key'
login_manager = LoginManager()
login_manager.init_app(app)
urllib3.disable_warnings()


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
            return render_template('add_object.html', form=form, message='Объект с таким номером уже зарегистрирован', title='Добавление объекта')
        if not form.about.data and not request.files['file']:
            return render_template('add_object.html', form=form, message='Добавьте описание объекта', title='Добавление объекта')
        reg = db_sess.query(Region).get(form.region.data)
        if not reg:
            return render_template('add_object.html', form=form,  message='Некорректный регион', title='Добавление объекта')
        text = ''
        if form.about.data:
            text = form.about.data + '\n'
        if request.files['file']:
            file = request.files['file']
            path = os.path.join('uploads', file.filename)
            file.save(path)
            if not get_text(path):
                os.remove(path)
                return render_template('add_object.html', form=form, message='Некорректный файл', title='Добавление объекта')
            text += get_text(path)
            os.remove(path)
        obj = Object(
            name=form.name.data,
            about=text,
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

    return render_template('add_object.html', form=form, title='Добавление объекта')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/show')
def show_objects():
    db_sess = db_session.create_session()
    objects = db_sess.query(Object).all()
    obj = [objects[randint(1, len(objects))] for _ in range(10)]
    return render_template('show_objects.html', obj=obj)


@app.route('/<int:object_id>', methods=['GET', 'POST'])
def get_object(object_id):
    db_sess = db_session.create_session()
    obj = db_sess.query(Object).get(object_id)
    form = AddCommentForm()
    comments = db_sess.query(Comment).filter(Comment.obj_id == object_id).all()
    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            obj_id=form.obj_id.data,
            creater_id=flask_login.current_user.id
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/{object_id}')
    if obj:
        coords = obj.coords
        if coords:
            get_photo(coords[1:-1])
        if obj.photo:
            try:
                res = requests.get(obj.photo, verify=False).content
                with open('static/photo/obj.png', 'wb') as file:
                    file.write(res)
                im = Image.open("static/photo/obj.png")
                out = im.resize((512, 512))
                out.save("static/photo/object.png")
            except:
                if os.path.isfile('static/photo/object.png'):
                    os.remove('static/photo/object.png')
                if os.path.isfile('static/photo/obj.png'):
                    os.remove('static/photo/obj.png')
        reg = db_sess.query(Region).get(obj.region)
        cat = db_sess.query(Category).get(obj.category)
        kind = db_sess.query(Kind).get(obj.kind)
        return render_template('object.html', obj=obj, comments=comments, region=reg.name, cat=cat.name, kind=kind.name, form=form)
    return jsonify({'error': 'object not found'})


@app.route('/del_obj/<int:object_id>', methods=['GET', 'POST'])
def delete_object(object_id):
    if not flask_login.current_user.is_authenticated or not flask_login.current_user.is_admin:
        return jsonify({'error': 'access denied'})
    db_sess = db_session.create_session()
    obj = db_sess.query(Object).get(object_id)
    if obj:
        db_sess.delete(obj)
        db_sess.commit()
        return redirect('/')
    return jsonify({'error': 'object not found'})


@app.route('/del_com/<int:comment_id>', methods=['GET', 'POST'])
def delete_comment(comment_id):
    db_sess = db_session.create_session()
    com = db_sess.query(Comment).get(comment_id)
    if com:
        if not flask_login.current_user.is_authenticated or not flask_login.current_user.is_admin or flask_login.current_user.id != com.creater_id:
            return jsonify({'error': 'access denied'})
        main_page_id = com.obj_id
        db_sess.delete(com)
        db_sess.commit()
        return redirect(f"/{main_page_id}")
    return jsonify({'error': 'comment not found'})


@app.route('/edit_obj/<int:object_id>', methods=['GET', 'POST'])
def edit_object(object_id):
    if not flask_login.current_user.is_authenticated or not flask_login.current_user.is_admin:
        return jsonify({'error': 'access denied'})
    db_sess = db_session.create_session()
    obj = db_sess.query(Object).get(object_id)
    if not obj:
        return jsonify({'error': 'object not found'})
    form = AddObject()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Object).filter(Object.reester_number == form.reester_number.data).first() and form.reester_number.data != obj.reester_number:
            return render_template('add_object.html', form=form, message='Объект с таким номером уже зарегистрирован')
        if not form.about.data and not request.files['file']:
            return render_template('add_object.html', form=form, message='Добавьте описание объекта', title='Изменение объекта')
        reg = db_sess.query(Region).get(form.region.data)
        if not reg:
            return render_template('add_object.html', form=form,  message='Некорректный регион', title='Изменение объекта')
        text = ''
        if form.about.data:
            text = form.about.data + '\n'
        if request.files['file']:
            file = request.files['file']
            path = os.path.join('uploads', file.filename)
            file.save(path)
            if not get_text(path):
                os.remove(path)
                return render_template('add_object.html', form=form, message='Некорректный файл', title='Изменение объекта')
            text += get_text(path)
            os.remove(path)
        obj.name = form.name.data
        obj.about = text
        obj.reester_number = form.reester_number.data
        obj.region = form.region.data
        obj.full_address = form.full_address.data
        obj.category = form.category.data
        obj.kind = form.kind.data
        obj.unesco = form.unesco.data
        obj.is_value = form.is_value.data
        obj.coords = form.coords.data
        local_obj = db_sess.merge(obj)
        db_sess.add(local_obj)
        db_sess.commit()
        return redirect(f'/{obj.id}')
    form.name.default = obj.name
    form.about.default = obj.about
    form.reester_number.default = obj.reester_number
    form.region.default = obj.region
    form.full_address.default = obj.full_address
    form.category.default = obj.category
    form.kind.default = obj.kind
    form.unesco.default = obj.unesco
    form.is_value.default = obj.is_value
    form.coords.default = obj.coords
    form.process()
    return render_template('add_object.html', form=form, title='Изменение объекта')


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = FindObjectForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.region == form.region.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.region == form.region.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif not bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and not form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.region == form.region.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.region == form.region.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and not bool(form.reester_number.data) and form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and bool(form.reester_number.data) and not form.region.data\
                and form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.category == form.category.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and not form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and not form.category.data and form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.kind == form.kind.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        elif bool(form.name.data) and bool(form.reester_number.data) and form.region.data\
                and form.category.data and not form.kind.data:
            obj = db_sess.query(Object).filter(Object.name.like(f"%{form.name.data}%"),
                                               Object.reester_number == form.reester_number.data,
                                               Object.region == form.region.data,
                                               Object.category == form.category.data,
                                               Object.unesco == form.unesco.data,
                                               Object.is_value == form.is_value.data).all()
        else:
            obj = None
        cache.set('obj', obj)
        return redirect('/objects')
    return render_template('search.html', form=form)


@app.route('/objects', methods=['GET', 'POST'])
def objects():
    obj = cache.get('obj')
    return render_template('objects.html', obj=obj)


def add_all_objects():
    db_sess = db_session.create_session()
    os.chdir('obj')
    l = os.listdir()
    for i in l:
        with open(i, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for j in data:
                name = j['nativeName']
                region = j['data']['general']['region']
                reg = db_sess.query(Region).get(region['id'])
                if not reg:
                    reg = Region(id=region['id'],
                                 name=region['value'])
                    db_sess.add(reg)
                    db_sess.commit()
                    
                reester_number = j['data']['general']['regNumber']
                category = j['data']['general']['categoryType']
                cat = db_sess.query(Category).get(category['id'])
                if not cat:
                    cat = Category(id=category['id'],
                                   name=category['value'])
                    db_sess.add(cat)
                    db_sess.commit()
                    
                kind = j['data']['general']['objectType']
                k = db_sess.query(Kind).get(kind['id'])
                if not k:
                    k = Kind(id=kind['id'],
                             name=kind['value'])
                    db_sess.add(k)
                    db_sess.commit()
                try:
                    about = j['data']['general']['createDate']
                except:
                    about = ''
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
                             region=region['id'],
                             reester_number=reester_number,
                             category=category['id'],
                             kind=kind['id'],
                             about=about,
                             unesco=unesco,
                             is_value=is_value,
                             full_address=full_address,
                             coords=str(coords),
                             photo=photo)
                db_sess.add(obj)
                db_sess.commit()


def get_photo(sel):
    geocoder_request = \
        f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={sel}&format=json"
    response = requests.get(geocoder_request)
    if response:
        toponym_coodrinates = \
            response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()

    map_request = \
        f"http://static-maps.yandex.ru/1.x/?ll={toponym_coodrinates[0]},{toponym_coodrinates[1]}&spn=0.005,0.005&l=map&pt={toponym_coodrinates[0]},{toponym_coodrinates[1]},comma"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    map_file = "static/photo/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)


def add_coords():
    db_sess = db_session.create_session()
    obj = db_sess.query(Object).filter(Object.full_address != '', Object.coords == '').all()
    for i in obj:
        try:
            address = str('+'.join(i.full_address.split(', '))).replace(' ', '+')
            geocoder_request = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}&format=json"
            response = requests.get(geocoder_request)
            if response:
                json_response = response.json()
                pos = (json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'])
                coords = ('[' + str(', '.join(pos.split())) + ']')
                print(f"{i.id}) {i.name} - {coords}")
                i.coords = coords
                db_sess.add(i)
                db_sess.commit()
        except Exception as e:
            print(f"{i.id} --- {e}")


def main():
    db_session.global_init('db/culture.db')
    port = int(os.environ.get("PORT", 5000))
    # app.run(port=5000, host='0.0.0.0')
    serve(app, port=port, host='0.0.0.0')
    # add_all_objects()
    # add_coords()


if __name__ == '__main__':
    main()