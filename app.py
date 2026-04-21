import os
import uuid

import flask_login
from flask import Flask, render_template, redirect
from dotenv import load_dotenv
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.users import User
from forms.login_form import LoginForm
from forms.register_form import RegisterForm

load_dotenv('.env')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

login_manager = LoginManager()
login_manager.init_app(app)


def check_log_in():
    if not current_user.is_authenticated:
        return True


@login_manager.user_loader
def user_loader(user_id):
    session = db_session.create_session()
    return session.get(User, user_id)


@app.route('/sign')
def sign():
    return render_template('sign.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(
            User.email == login_form.email.data
        ).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me)
            return redirect('/')
        return render_template('login.html', form=login_form, message='Ошибка входа')
    return render_template('login.html', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == register_form.email.data).first()
        if user:
            return render_template('register.html', form=register_form, message='Почта уже занята')
        user = session.query(User).filter(User.username == register_form.username.data).first()
        if user:
            return render_template('register.html', form=register_form, message='Никнейм уже занят')
        avatar_filename = uuid.uuid4().hex + '.png'
        with open('static/images/avatars/' + avatar_filename, mode='wb') as avatar_file:
            avatar_file.write(register_form.avatar.data.read())
        new_user = User(
            username=register_form.username.data, surname=register_form.surname.data, name=register_form.name.data,
            age=register_form.age.data, description=register_form.description.data, avatar='static/images/avatars/' + avatar_filename,
            email=register_form.email.data, hashed_password=register_form.hashed_password.data, is_deleted=False
        )
        new_user.hash_password(new_user.hashed_password)
        session.add(new_user)
        session.commit()
        login_user(new_user)
        return redirect('/')
    return render_template('register.html', form=register_form)


@app.route('/')
def index():
    if check_log_in():
        return redirect('/sign')
    return render_template('base.html', title='ZeK')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    db_session.global_init('db/Zek.db')
    app.run('127.0.0.1', 8080)

