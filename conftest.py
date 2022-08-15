import pytest
import asyncio
import os

from typing import Callable
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from dotenv import load_dotenv

load_dotenv('.env')


test_user = {
        'login': 'awesome test',
        'email': 'AwesomeTest@mail.ru',
        'password': '1234567890XxX',
        'inn': 2304068734,
        'fio': 'This is test user',
        'phone': '+79883258832',
        'user_type': 'client'
        }

test_update_data = {
        'inn': 4253025966,
        'fio': 'This new fio test'
        }


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
            await session.flush()
            await session.rollback()


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
async def async_client_auth(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/api") as ac:
        response = await ac.post('/user/login', json={
                'login': test_user['login'],
                'password': test_user['password']
            })
        if response.status_code == 404:
            response = await ac.post('/user/signup', json=test_user)
        ac.headers['Authorization'] = response.json().get('Authorization')
        yield ac

