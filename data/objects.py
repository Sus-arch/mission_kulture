import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Object(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'objects'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    about = sqlalchemy.Column(sqlalchemy.String)
    reester_number = sqlalchemy.Column(sqlalchemy.String, unique=True)
    region = sqlalchemy.Column(sqlalchemy.String)
    full_address = sqlalchemy.Column(sqlalchemy.String)
    category = sqlalchemy.Column(sqlalchemy.String)
    kind = sqlalchemy.Column(sqlalchemy.String)
    unesco = sqlalchemy.Column(sqlalchemy.BOOLEAN)
    is_valuable = sqlalchemy.Column(sqlalchemy.BOOLEAN)
