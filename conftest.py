import pytest
import asyncio
import os

from typing import Callable
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from dotenv import load_dotenv

from db.queries.users_q import delete_user_from_db

load_dotenv('.env')

@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def db_session() -> AsyncSession:
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with engine.begin() as connection:
        async with async_session(bind=connection) as session:
            yield session
            #await session.flush()
            #await session.rollback()


@pytest.fixture()
async def get_session() -> AsyncSession:
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session

@pytest.fixture()
def override_get_session(get_session: AsyncSession):
    async def _override_get_session():
        yield get_session

    return _override_get_session


@pytest.fixture()
def app(override_get_session: Callable):
    from db.session import get_session
    from app import app as fast_app

    fast_app.dependency_overrides[get_session] = override_get_session
    return fast_app


@pytest.fixture()
async def async_client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://127.0.0.1/api") as ac:
        yield ac

@pytest.fixture()
async def async_client_auth(app: FastAPI, test_register_user, get_session):
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/api") as ac:
        response = await ac.post('/user/login', json={
                'login': test_register_user['login'],
                'password': test_register_user['password']
            })
        if response.status_code == 404:
            response = await ac.post('/user/signup', json=test_register_user)
        ac.headers['Authorization'] = response.json().get('Authorization')
        yield ac
    await delete_user_from_db(get_session, test_register_user['login'])


@pytest.fixture()
async def async_client_deleted_user(get_session, app: FastAPI, test_delete_user, delete_user_data):
    async with AsyncClient(app=app, base_url='http://127.0.0.1:8000/api') as ac:
        response = await ac.post('/user/login', json=test_delete_user)
        if response.status_code == 404:
            response = await ac.post('user/signup', json=test_delete_user)
        ac.headers['Authorization'] = response.json().get('Authorization')
        await ac.post('/user/delete_user', json=delete_user_data)
        yield ac
        await delete_user_from_db(get_session, test_delete_user['login'])


@pytest.fixture()
def delete_user_data():
    return {
                'reason_deleted': 'license',
                'delete_text': 'Это причина удаления по отзыву лицензии'
                }
@pytest.fixture()
def delete_user_bad_datas():
    return (
                {
                    'reason_deleted': 'sjnsibg',
                    'delete_text': 'Ошибочная причина удаения аккаунта'
                },
                {
                    'reason_deleted': 'bank',
                    'delete_text': 87542784527845
                }
            )

@pytest.fixture()
def test_register_user():
    return {
                'login': 'awesome tester',
                'email': 'AwesomeTestered@mail.ru',
                'password': '1234567890XxX',
                'inn': 2304068734,
                'fio': 'This is test user',
                'phone': '+79884258833',
                'user_type': 'client'
            }

@pytest.fixture()
def test_user():
    return {
                'login': 'awesome test',
                'email': 'AwesomeTest@mail.ru',
                'password': '1234567890XxX',
                'inn': 2304068734,
                'fio': 'This is test user',
                'phone': '+79889258893',
                'user_type': 'client'
            }

@pytest.fixture()
def test_update_data_user():
    return {
                'inn': 7816704903,
                'fio': 'this update fio'
            }

@pytest.fixture()
def test_delete_user():
    return {
                'login': 'awesome deleted user',
                'email': 'AwesomeDeletedUser@mail.ru',
                'password': '123424524352XxX',
                'inn': 2304068734,
                'fio': 'This test deleted user',
                'phone': '+79884458844',
                'user_type': 'client'
           }
