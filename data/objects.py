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
    region = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("region.id"))
    full_address = sqlalchemy.Column(sqlalchemy.String)
    category = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("category.id"))
    kind = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("kind.id"))
    unesco = sqlalchemy.Column(sqlalchemy.BOOLEAN)
    is_value = sqlalchemy.Column(sqlalchemy.BOOLEAN)
    coords = sqlalchemy.Column(sqlalchemy.String)
    photo = sqlalchemy.Column(sqlalchemy.String)

    categories = orm.relation('Category')
    regions = orm.relation('Region')
    kinds = orm.relation('Kind')
