from sqlalchemy import Column, Integer, String, Boolean, orm, ForeignKey

from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    members = Column(String)
    messages = Column(String)
