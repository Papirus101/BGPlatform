from sqlalchemy.orm import relationship
from db.base import Base
from sqlalchemy import Column, BIGINT, Integer, VARCHAR, ForeignKey, Boolean, event
from sqlalchemy_utils import ChoiceType
from db.models.banks import Banks

from db.models.users import User

QUARTER_CHOICE = [
    ('profit', 'прибыль'),
    ('lesion', 'убыток')
]


class BGTypes(Base):
    __tablename__ = 'bg_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    description = Column(VARCHAR)


class WorksSpecifics(Base):
    __tablename__ = 'bg_words_specifics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    description = Column(VARCHAR)


class BanksRequest(Base):
    __tablename__ = 'bg_request_banks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank = Column(ForeignKey(Banks.id, ondelete='CASCADE'), nullable=False)
    request = Column(ForeignKey('bg_request.id', ondelete='CASCADE'), nullable=False)


class CompanyTypes(Base):
    __tablename__ = 'company_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)


class BGRequest(Base):
    __tablename__ = 'bg_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    inn = Column(BIGINT)
    purchase_number = Column(VARCHAR, default=None, nullable=True)
    purchase_name = Column(VARCHAR, default=None, nullable=True)
    amount = Column(Integer)
    days = Column(Integer)
    bg_type_id = Column(ForeignKey(BGTypes.id, ondelete='CASCADE'), nullable=False, default=1)
    last_quarter = Column(ChoiceType(QUARTER_CHOICE))
    lesion_amount = Column(Integer, default=0)
    specifics_of_work_id = Column(ForeignKey(WorksSpecifics.id, ondelete='CASCADE'), nullable=False, default=1)

    # PARSE INFO
    company_name = Column(VARCHAR, default=None, nullable=True)
    company_ogrn = Column(VARCHAR, default=None, nullable=True)
    company_opf_code = Column(VARCHAR, default=None, nullable=True)
    company_address = Column(VARCHAR, default=None, nullable=True)
    company_date_register = Column(VARCHAR, default=None, nullable=True)
    company_rnp = Column(Boolean, default=False)
    company_auth_capital = Column(BIGINT, default=0)
    company_bankrupt = Column(Boolean, default=False)
    company_last_revenue_sum = Column(BIGINT, default=0)
    company_tax_arrears_sum = Column(BIGINT, default=0)
    company_arbitration_cases_sum = Column(BIGINT, default=0)
    company_executed_lists_sum = Column(BIGINT, default=0)
    company_mass_address = Column(Boolean, default=False)
    company_resident = Column(Boolean, default=True)
    company_fz_id = Column(Integer, ForeignKey('fz_types.id', ondelete='CASCADE'), nullable=True)

    company_type_id = Column(ForeignKey(CompanyTypes.id, ondelete='CASCADE'), nullable=True)
    action_info = Column(VARCHAR)  # Показатель процесса сбора информации и скоринга
    is_ready = Column(Boolean, default=False)

    bg_info = relationship(BGTypes, backref='bg_info_report')
    company_types = relationship(CompanyTypes, backref='bg_company_type')
    company_fz = relationship('FZTypes', backref='bg_fz_company')
    user = relationship(User, backref='bg_request_owner')
    specifics_of_work = relationship(WorksSpecifics, backref='bg_specifics_of_worf')
    banks_ids = relationship('Banks', secondary=BanksRequest.__tablename__, backref='banks_request')


@event.listens_for(BGTypes.__table__, "after_create")
def insert_test_datas_bg_type(mapper, connection, *args, **kwargs):
    bg_types = BGTypes.__table__
    connection.execute(bg_types.insert().values(name='Тест', description='test'))

@event.listens_for(WorksSpecifics.__table__, "after_create")
def insert_test_datas_work_specifics(mapper, connection, *args, **kwargs):
    specific = WorksSpecifics.__table__
    connection.execute(specific.insert().values(name='тестовая спецификация', description='тест описания'))

@event.listens_for(CompanyTypes.__table__, 'after_create')
def insert_test_datas_company_types(mapper, connection, *args, **kwargs):
    types = CompanyTypes.__table__
    connection.execute(types.insert().values(name='ООО'))
    connection.execute(types.insert().values(name='ИП'))

