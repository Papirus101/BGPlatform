import datetime
from sqlalchemy.exc import NoResultFound, DBAPIError, MultipleResultsFound
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload
from db.models.banks import Banks, FZTypes

from db.models.bg_request import BGRequest, BGTypes, WorksSpecifics

from db.queries.raw_sql import banks_request_sql, request_info_sql


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
        sql = request_info_sql.format(request_id=request_id, user_id=user_id)
        try:
            data = await session.execute(sql)
            data = data.all()
        except (NoResultFound, MultipleResultsFound):
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


async def update_request_info(db_session, request_id: int, **kwargs):
    """ Функция для обновления информации о заявке парсером """
    async with db_session() as session:
        request = update(BGRequest).where(BGRequest.id == request_id).values(**kwargs)
        await session.execute(request)
        await session.commit()


async def get_banks_with_terms(session, request):
    """ Возвращает список подходящих банков """
    company_days = datetime.datetime.strptime(request.company_date_register, '%d.%m.%Y')
    company_days = (datetime.datetime.today() - company_days).days
    sql = banks_request_sql.format(
                request_days=request.days,
                request_amount=request.amount,
                request_company_days=company_days,
                request_capital=request.company_auth_capital,
                request_lession_quarterly=request.lesion_amount,
                request_execution_amount=request.company_executed_lists_sum,
                request_debt_amount=request.company_tax_arrears_sum,
                request_bg_type=request.bg_info.id,
                request_fz_type=request.company_fz.id,
                request_company_type=request.company_types.id if request.company_types is not None else 0,
                request_last_revenue=request.company_last_revenue_sum)
    banks = await session.execute(sql)
    banks = banks.all()
    return banks


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
        banks = await get_banks_with_terms(session, request)
        total_banks = []
        for bank in banks:
            if not bank.mass_address and request.company_mass_address:
                continue
            if not bank.bankrupt and request.company_bankrupt:
                if bank.rezident and not request.company_resident:
                    continue
            if not bank.rnp and request.company_rnp:
                continue
            total_banks.append(await session.get(Banks, bank.id))
        request.banks_ids = total_banks
        await session.commit()
        return banks


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
