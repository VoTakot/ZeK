from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import EmailField, PasswordField, SubmitField, ValidationError
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length
import re


def username_validator(form, field):
    if not re.match(r'^[a-zA-Z0-9]+$', field.data):
        raise ValidationError('Поле должно содержать только латинские буквы и цифры')


class EditForm(FlaskForm):
    surname = StringField('Фамилия')
    name = StringField('Имя')
    age = IntegerField('Возраст')
    username = StringField('Никнейм', validators=[username_validator, Length(min=6, max=20)])
    email = EmailField('Email')
    description = StringField('Описание', validators=[Length(max=500)])
    avatar = FileField('Аватар')
    hashed_password = PasswordField('Пароль', validators=[Length(min=8, max=20)])
    submit = SubmitField('Изменить', )