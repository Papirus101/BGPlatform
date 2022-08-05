from sqlalchemy.orm import relationship

from db.base import Base
from sqlalchemy import Column, BIGINT, VARCHAR, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy_utils import ChoiceType

USER_TYPES = [
    ('client', 'Клиент'),
    ('agent', 'Агент'),
    ('bank', 'Банк'),
    ('admin', 'Администратор')
]


REASON_DELETED = [
    ('bank', 'По требованию банка'),
    ('license', 'Отзыв лицензии'),
    ('conflict', 'Возникла конфликтная ситуация'),
    ('another', 'Другая причина')
]


# class AuctionBrokers(Base):
#     __tablename__ = 'auction_brokers'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     broker = Column(ForeignKey('users.id', ondelete='CASCADE'))
#     auction = Column(ForeignKey('auctions.id', ondelete='CASCADE'))
#
#
# class AuctionOffers(Base):
#     __tablename__ = 'auction_offers'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     auction_id = Column(ForeignKey('auctions.id', ondelete='CASCADE'), nullable=False)
#     offerer = Column(ForeignKey('banks.id', ondelete='CASCADE'), nullable=True)
#     custom_offerer = Column(ForeignKey('custom_offers.id', ondelete='CASCADE'), nullable=True)
#
#
# class Banks(Base):
#     __tablename__ = 'banks'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(VARCHAR)
#     bid = Column(Integer)
#     conditions_of_brokers = Column(Integer)
#
#     broker = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
#
#
# class CustomOffer(Base):
#     __tablename__ = 'custom_offers'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     amount = Column(Integer)
#     broker_name = Column(VARCHAR)
#     bank_name = Column(VARCHAR)
#     opening_account = Column(Boolean, default=False)
#     deposit = Column(Boolean, default=False)
#     pledge = Column(Boolean, default=False)
#     guarantee = Column(Boolean, default=False)
#
#
# class Auction(Base):
#     __tablename__ = 'auctions'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     request_id = Column(ForeignKey('bg_request.id', ondelete='CASCADE'), nullable=False)
#     finish = Column(DateTime)
#     count_change_finish_data = Column(Integer, default=0)
#     all_brokers = Column(Boolean, default=True)
#
#     brokers = relationship('User', secondary=AuctionBrokers.__tablename__, backref='Brokers')


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

    deleted = Column(Boolean, default=False)
    reason_deleted = Column(ChoiceType(REASON_DELETED))
    delete_text = Column(VARCHAR, default=None, nullable=True)
