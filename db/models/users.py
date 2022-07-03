from db.base import Base
from sqlalchemy import Column, BIGINT, VARCHAR, Integer
from sqlalchemy_utils import ChoiceType

USER_TYPES = [
    ('client', 'Клиент'),
    ('agent', 'Агент'),
    ('bank', 'Банк'),
    ('admin', 'Администратор')
]


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(VARCHAR, unique=True)
    login = Column(VARCHAR, unique=True)
    password = Column(VARCHAR)
    inn = Column(BIGINT)
    fio = Column(VARCHAR)
    phone = Column(VARCHAR)
    name_organization = Column(VARCHAR, default=None)
    user_type = Column(ChoiceType(USER_TYPES))
    photo = Column(VARCHAR)
