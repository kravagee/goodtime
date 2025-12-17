import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, TEXT, Date
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    last_name = Column(String, nullable=True)

    owned_organizations = relationship('Organization', back_populates='owner')

    owned_orgs = Column(TEXT, nullable=True)
    birthday = Column(Date, default=datetime.datetime.today())
    hashed_password = Column(String, nullable=False)
    registred_on = Column(TEXT, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)