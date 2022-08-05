from sqlalchemy import BIGINT, Integer, Boolean, VARCHAR, Column, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class BankFzTypes(Base):
    __tablename__ = 'bank_fz_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'))
    fz_type_id = Column(Integer, ForeignKey('fz_types.id', ondelete='CASCADE'))


class BankCompanyTypes(Base):
    __tablename__ = 'bank_company_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_id = Column(ForeignKey('banks.id', ondelete='CASCADE'), nullable=False)
    company_type_id = Column(ForeignKey('company_types.id', ondelete='CASCADE'), nullable=False)


class BGTypesBank(Base):
    __tablename__ = 'bank_bg_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'))
    bg_type_id = Column(Integer, ForeignKey('bg_types.id', ondelete='CASCADE'))


class BankValuteTypes(Base):
    __tablename__ = 'bank_valute_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_id = Column(Integer, ForeignKey('banks.id', ondelete='CASCADE'))
    valute_type_id = Column(Integer, ForeignKey('valute_types.id', ondelete='CASCADE'))

class ValuteTypes(Base):
    __tablename__ = 'valute_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)


class FZTypes(Base):
    __tablename__ = 'fz_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)


class Banks(Base):
    __tablename__ = 'banks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    
    fz_types = relationship('FZTypes', secondary=BankFzTypes.__tablename__, backref='fz_types_bank')
    bg_types = relationship('BGTypes', secondary=BGTypesBank.__tablename__, backref='bg_types_bank')
    min_guarante = Column(Integer, default=0)
    max_guarante = Column(BIGINT, default=2147483647)
    min_days = Column(Integer, default=1)
    max_days = Column(Integer, default=900)
    company_type = relationship('CompanyTypes', secondary=BankCompanyTypes.__tablename__, backref='comany_types_bank')
    min_company_dates = Column(Integer, default=1)
    authorized_capital = Column(BIGINT, default=2147483647)
    mass_address = Column(Boolean, default=True)
    percent_revenue = Column(Integer, default=1) # отдельная логика
    active = Column(Boolean, default=False) # отдельная логика
    bankrupt = Column(Boolean, default=True)
    lesion_year_amount = Column(BIGINT, default=0)
    lesion_quarterly_amount = Column(BIGINT, default=0)
    execution_lists_amount = Column(BIGINT, default=0)
    amount_debt_on_taxes_and_fees = Column(BIGINT, default=0)
    rezident = Column(Boolean, default=False) # отдельная логика
    rnp = Column(Boolean, default=False)
    region = Column(VARCHAR, nullable=False, default='') # отдельная логика
    valute_types = relationship('ValuteTypes', secondary=BankValuteTypes.__tablename__, backref='bank_valute_type') # отдельная логика
    stavka = Column(Integer, default=0)
    brokers_terms = Column(Integer, default=0)
    manager = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), default=None, nullable=True)
    bg_system_name = Column(VARCHAR, default=None, nullable=True)
    bg_system_link = Column(VARCHAR, default=None, nullable=True)


