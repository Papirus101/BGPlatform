import datetime
from sqlalchemy.exc import NoResultFound, DBAPIError
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from db.models.banks import Banks, FZTypes

from db.models.bg_request import BGRequest, BGTypes, WorksSpecifics



async def add_new_bg_request(db_session,
                             user_id: int,
                             purchase_number: int,
                             inn: int,
                             amount: int,
                             days: int,
                             bg_type: int,
                             last_quarter: str,
                             specifics_of_work: int,
                             lesion_amount: int = 0):
    """Функция для добавлеия новой заявки в базу"""
    async with db_session() as session:
        new_bg_request = BGRequest(user_id=user_id,
                                   purchase_number=purchase_number,
                                   inn=inn,
                                   amount=amount,
                                   days=days,
                                   bg_type_id=bg_type,
                                   last_quarter=last_quarter,
                                   specifics_of_work_id=specifics_of_work,
                                   lesion_amount=lesion_amount)
        try:
            session.add(new_bg_request)
            await session.flush()
            await session.commit()
        except DBAPIError:
            return {'error': 'INN invalid'}
        return new_bg_request


async def get_specifics_works_q(db_session):
    async with db_session() as session:
        sql = select(WorksSpecifics.id, WorksSpecifics.name, WorksSpecifics.description)
        data = await session.execute(sql)
        data = data.all()
    return data


async def get_bg_types_q(db_session):
    async with db_session() as session:
        sql = select(BGTypes.id, BGTypes.name, BGTypes.description)
        data = await session.execute(sql)
        data = data.all()
    return data



async def get_user_request_query(db_session, user_id: int, request_id: int):
    """ Получение конкретной заявки пользователя """
    async with db_session() as session:
        sql = select(BGRequest).options(
                        selectinload(BGRequest.banks_ids)
                        ).where(BGRequest.user_id == user_id, BGRequest.id == request_id)
        data = await session.execute(sql)
        try:
            data = data.one()
        except NoResultFound:
            return None
    return data[0]


async def get_user_requests_query(db_session, user_id: int):
    """ Получение всех заявок пользователя """
    async with db_session() as session:
        sql = select(BGRequest.id, BGRequest.purchase_number, BGRequest.amount, BGRequest.days,
                     BGRequest.company_name, BGRequest.is_ready).where(
            BGRequest.user_id == user_id).order_by(BGRequest.id)
        data = await session.execute(sql)
        data = data.all()
    return data


async def test_query(db_session):
    async with db_session() as session:
        sql = select(BGRequest).options(
                selectinload(BGRequest.company_types),
                selectinload(BGRequest.specifics_of_work),
                selectinload(BGRequest.banks_ids),
                selectinload(BGRequest.company_fz)
                ).where(BGRequest.id == 3)
        
        data = await session.execute(sql)
        data = data.one()


async def update_request_info(db_session, request_id: int, **kwargs):
    """ Функция для обновления информации о заявке парсером """
    async with db_session() as session:
        request = update(BGRequest).where(BGRequest.id == request_id).values(**kwargs)
        await session.execute(request)
        await session.commit()


async def bg_request_banks_insert(db_session, request_id: int):
    """ Функция для установки банков, готовых выдать деньги """
    async with db_session() as session:
        sql = select(BGRequest).options(
                selectinload(BGRequest.company_types),
                selectinload(BGRequest.specifics_of_work),
                selectinload(BGRequest.banks_ids),
                selectinload(BGRequest.company_fz),
                selectinload(BGRequest.bg_info)
                ).where(BGRequest.id == request_id)
        try:
            request = await session.execute(sql)
            request = request.one()
        except NoResultFound:
            return {"error": 'not request found'}
        request = request[0]
        sql = select(Banks).options(
                selectinload(Banks.fz_types),
                selectinload(Banks.bg_types),
                selectinload(Banks.company_type),
                selectinload(Banks.valute_types)
                )
        data = await session.execute(sql)
        data = data.all()
        sql = select(Banks).options(
                selectinload(Banks.fz_types),
                selectinload(Banks.bg_types),
                selectinload(Banks.company_type),
                selectinload(Banks.valute_types)
                )
        data = await session.execute(sql)
        total_banks = []
        data = data.all()
        for bank in data:
            bank = bank[0]
            if len(bank.fz_types) > 0 and request.company_fz not in bank.fz_types:
                for fz in bank.fz_types:
                    print(request.company_fz.id, fz.id)
                    print(bank.name, fz.id, fz.name)
                print('fz')
                continue
            if len(bank.bg_types) > 0 and request.bg_info not in bank.bg_types:
                print('bg')
                continue
            if bank.min_guarante is not None and bank.max_guarante is not None and \
                    bank.min_guarante > request.amount or bank.max_guarante < request.amount:
                continue
            if bank.min_days is not None and bank.max_days is not None and \
                    bank.min_days > request.days or bank.max_days < request.days:
                print('min max days', request.days, bank.min_days, bank.max_days)
                continue
            # if len(bank.company_type) > 0 and request.company_types not in bank.company_type:
            #    print('company_type')
            #    continue
            company_days = datetime.datetime.strptime(request.company_date_register, '%d.%m.%Y')
            company_days = datetime.datetime.today() - company_days
            if company_days.days < bank.min_company_dates:
                print('company_days')
                continue
            if request.company_auth_capital < bank.authorized_capital:
                print('auth cap')
                continue
            if not bank.mass_address:
                if request.company_mass_address:
                    continue
            if bank.percent_revenue is not None and bank.percent_revenue > 0:
                company_revenue = request.company_last_revenue_sum * (bank.percent_revenue / 100)
                if company_revenue > request.amount:
                    continue
            if not bank.bankrupt and request.company_bankrupt:
                continue
            if bank.lesion_quarterly_amount > 0 and request.lesion_amount > bank.lesion_quarterly_amount:
                continue
            if bank.execution_lists_amount > 0 and bank.execution_lists_amount > request.company_executed_lists_sum:
                continue
            if bank.amount_debt_on_taxes_and_fees > request.company_tax_arrears_sum:
                continue
            if bank.rezident and not request.company_resident:
                continue
            if not bank.rnp and request.company_rnp:
                continue
            total_banks.append(bank)
        request.banks_ids = total_banks
        await session.commit()
        return data


async def get_fz_type_by_name(db_session, fz_name: str):
    """ Получаем fz для установки foreign key в заявку """
    async with db_session() as session:
        sql = select(FZTypes.id).where(FZTypes.name.like(fz_name.strip()))
        try:
            data = await session.execute(sql)
            data = data.one()
            return data[0]
        except NoResultFound:
            pass
        return None
