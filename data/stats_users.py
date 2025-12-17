from sqlalchemy import Column, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class StatsUser(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'stats_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    events_count = Column(Integer, nullable=True)
    hours_count = Column(Float, nullable=True)
    orgs_owned = Column(Integer, nullable=True)

    user = relationship('User')