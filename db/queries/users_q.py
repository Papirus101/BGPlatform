from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError,
    NoResultFound,
    DBAPIError,
    PendingRollbackError,
)
from sqlalchemy import delete, select, update

from db.models.users import User


async def create_new_user(session, **kwargs):
    new_user = User(**kwargs)
    await session.merge(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(400, "Login or email is already exists")
    except DBAPIError:
        raise HTTPException(400, "INN invalid")


async def check_user_created(session, login: str):
    sql = select(User).where(User.login == login)
    data = await session.execute(sql)
    try:
        data.one()
        raise HTTPException(400, "Login or email alredy exists")
    except NoResultFound:
        pass


async def get_user_by_login(session, login: str, deleted: bool = False):
    sql = select(User).where(User.login == login, User.deleted == deleted)
    try:
        data = await session.execute(sql)
        data = data.one()
        data = data[0]
    except NoResultFound:
        await session.rollback()
        raise HTTPException(404, "user not found")
    return data


async def update_user_info_q(session, login: str, **kwargs):
    sql = update(User).where(User.login == login).values(**kwargs)
    try:
        await session.execute(sql)
        await session.commit()
    except DBAPIError:
        await session.rollback()
        raise HTTPException(400)


async def delete_user_from_db(session, login: str):
    sql = delete(User).where(User.login == login)
    await session.execute(sql)
    await session.commit()
