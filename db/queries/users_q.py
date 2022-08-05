from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.models.users import User


async def create_new_user(
        db_session: AsyncSession,
        **kwargs
):
    async with db_session() as session:
        new_user = User(**kwargs)
        await session.merge(new_user)
        try:
            await session.commit()
        except IntegrityError:
            return {'error': 'Login or email is already exists'}


async def get_user_by_login(db_session: AsyncSession,
                            login: str):
    async with db_session() as session:
        sql = select(User).where(User.login == login, User.deleted == False)
        try:
            data = await session.execute(sql)
            data = data.one()
            data = data[0]
        except NoResultFound:
            raise HTTPException(404, {'error': 'user not found'})
        return data


async def update_user_info_q(db_session: AsyncSession, login: int, **kwargs):
    async with db_session() as session:
        sql = update(User).where(User.login == login).values(**kwargs)
        await session.execute(sql)
        await session.commit()

