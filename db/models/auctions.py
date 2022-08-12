from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from db.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, BIGINT, VARCHAR
from sqlalchemy.sql import func


USER_TYPES = [
    ('client', 'Клиент'),
    ('agent', 'Агент'),
    ('bank', 'Банк'),
    ('admin', 'Администратор')
]

TERM_TYPES = [
        ('checking_account', 'Обязательное открытие расчетного счёта'),
        ('deposit', 'Требуется депозит'),
        ('zalog', 'Требуется залог'),
        ('guarantee', 'Требуется поручительство')
]


class AuctionMembers(Base):
    __tablename__ = 'auction_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    memeber = Column(ForeignKey('User', ondelete='CASCADE'), nullable=False)
    auction = Column(ForeignKey('Auction', ondelete='CASCADE'), nullable=False)


class AuctionOfferTerms(Base):
    __tablename__ = 'auction_offer_terms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer = Column(ForeignKey('AuctionOffers', ondelete='CASCADE'))
    term_type = Column(ChoiceType(TERM_TYPES))


class AuctionOffers(Base):
    __tablename__ = 'auction_offers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auction = Column(ForeignKey('Acution', ondelete='CASCADE'))
    amount = Column(Integer)
    user_type = Column(ChoiceType(USER_TYPES))
    broker_name = Column(VARCHAR, nullable=True)
    bank_name = Column(VARCHAR, nullable=True)
    terms_bg = relationship('AuctionOfferTerms', secondary=AuctionOfferTerms.__tablename__, backref='terms_auction')


class AuctionDateEdits(Base):
    __tablename__ = 'auction_date_end_edit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auction = Column(ForeignKey('Auction', ondelete='CASCADE'))
    date_end = Column(DateTime(timezone=True))


class Auction(Base):
    __tablename__ = 'auction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    request = Column(ForeignKey('BGRequests', ondelete='CASCADE'), nullable=False)
    members = relationship('User', secondary=AuctionMembers.__tablename__, backref='members_auction')
    date_start = Column(DateTime(timezone=True), server_default=func.now())
    date_stop = Column(DateTime(timezone=True))
    date_end = Column(ForeignKey('AuctionDateEdits', ondelete='CASCADE'), nullable=True)
    offers = relationship('AuctionOffers', secondary=AuctionOffers.__tablename__, backref='offers_auction')


