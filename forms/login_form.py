from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8, max=20, message='Длинна от 8 до 20 символов')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')