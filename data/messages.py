from sqlalchemy import Column, Integer, String, Boolean, orm, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    message = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))
    user = orm.relationship('User')
    created_at = Column(DateTime, default=datetime.now)
