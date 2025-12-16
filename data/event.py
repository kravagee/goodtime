import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, TEXT, Float
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Event(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.datetime.now)

    organization_id = Column(Integer, ForeignKey('organizations.id'))
    orgs = relationship('Organization', back_populates='events')

    saint_persons_list = Column(TEXT, nullable=True)
    hours = Column(Float, nullable=False)