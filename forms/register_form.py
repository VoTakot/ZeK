from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, ValidationError, FileField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length
import re


def username_validator(form, field):
    if not re.match(r'^[a-zA-Z0-9]+$', field.data):
        raise ValidationError('Поле должно содержать только латинские буквы и цифры')


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), username_validator, Length(min=6, max=20)])
    email = EmailField('Email', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired(), Length(max=40)])
    avatar = FileField('Аватар', validators=[DataRequired()])
    hashed_password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация')