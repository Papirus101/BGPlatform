import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from db.base import Base
from db.models import users, bg_request, banks

from dotenv import load_dotenv

load_dotenv('.env')

engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


sync_engin = create_engine(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
if not database_exists(sync_engin.url):
    create_database(sync_engin.url)
    Base.metadata.create_all(bind=sync_engin)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
