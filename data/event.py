from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, TEXT, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Event(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(TEXT, nullable=True)
    city = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)

    organization_id = Column(Integer, ForeignKey('organizations.id'))
    orgs = relationship('Organization', back_populates='events')

    saint_persons_list = Column(TEXT, nullable=True)
    saint_persons_count = Column(Integer, nullable=True)
    hours = Column(Float, nullable=False)
    done = Column(Boolean, default=False)