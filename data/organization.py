from sqlalchemy import Column, Integer, String, ForeignKey, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Organization(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    owner = relationship('User', back_populates='owned_organizations')
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    events_list = Column(TEXT, nullable=True)
    events = relationship('Event', back_populates='orgs')
