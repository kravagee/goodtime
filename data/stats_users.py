from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class StatsUsers(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'stats_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    events_count = Column(Integer, nullable=True)
    hours_count = Column(Integer, nullable=True)
    orgs_owned = Column(Integer, nullable=True)

    user = relationship('User')