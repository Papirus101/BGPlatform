from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.users import User


async def create_new_user(
        db_session: AsyncSession,
        email: str,
        login: str,
        password: str,
        inn: int,
        fio: str,
        phone: str,
        user_type: str
):
    async with db_session() as session:
        new_user = User(email=email,
                        login=login,
                        password=password,
                        inn=inn,
                        fio=fio,
                        phone=phone,
                        user_type=user_type)
        await session.merge(new_user)
        try:
            await session.commit()
        except IntegrityError:
            return {'error': 'Login or email is already exists'}


async def get_user_by_login(db_session: AsyncSession,
                            login: str):
    async with db_session() as session:
        sql = select(User).where(User.login == login)
        try:
            data = await session.execute(sql)
            data = data.one()
            data = data[0]
        except NoResultFound:
            data = None
        return data
