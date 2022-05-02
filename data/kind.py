import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Kind(SqlAlchemyBase):
    __tablename__ = 'kind'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)