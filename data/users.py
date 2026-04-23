from sqlalchemy import Column, Integer, String, Boolean, orm
from hashlib import md5

from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    surname = Column(String)
    name = Column(String)
    age = Column(Integer)
    description = Column(String)
    avatar = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    friends = Column(String)
    is_deleted = Column(Boolean)

    def hash_password(self, password):
        self.hashed_password = md5(password.encode()).hexdigest()

    def check_password(self, password):
        return self.hashed_password == md5(password.encode()).hexdigest()
