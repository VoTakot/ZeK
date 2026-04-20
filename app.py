import os

import flask_login
from flask import Flask, render_template, redirect
from dotenv import load_dotenv
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.users import User
from forms.login_form import LoginForm

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


@app.route('/')
def index():
    if check_log_in():
        return redirect('/sign')
    return render_template('base.html', title='ZeK')


@app.route('/video')
def


if __name__ == '__main__':
    db_session.global_init('db/Zek.db')
    app.run('127.0.0.1', 8080)
