import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Projects(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'applications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    fullnames = sqlalchemy.Column(sqlalchemy.String, nullable=False, default=False)
    heading = sqlalchemy.Column(sqlalchemy.String, nullable=False, default=False)
    annotation = sqlalchemy.Column(sqlalchemy.String, nullable=False, default=False)

    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    is_confirmed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)

    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)

    image = sqlalchemy.Column(sqlalchemy.String)
    docx = sqlalchemy.Column(sqlalchemy.String)

    like = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    dislike = sqlalchemy.Column(sqlalchemy.Integer, default=0)


    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
