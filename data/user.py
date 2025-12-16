import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)

    owned_organizations = relationship('Organization', back_populates='owner')

    birthday = Column(DateTime, default=datetime.datetime.now)
    hashed_password = Column(String, nullable=False)
    registred_on = Column(TEXT, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)