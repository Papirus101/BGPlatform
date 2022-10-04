import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from db.base import Base

from dotenv import load_dotenv

from settings import ASYNC_DB_LINK, SYNC_DB_LINK

load_dotenv(".env")

engine = create_async_engine(
    ASYNC_DB_LINK.format(
        db_user=os.getenv("DB_USER"),
        db_pass=os.getenv("DB_PASS"),
        db_host=os.getenv("DB_HOST"),
        db_port=os.getenv("DB_PORT"),
        db_name=os.getenv("DB_NAME"),
    )
)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


sync_engin = create_engine(
    SYNC_DB_LINK.format(
        db_user=os.getenv("DB_USER"),
        db_pass=os.getenv("DB_PASS"),
        db_host=os.getenv("DB_HOST"),
        db_port=os.getenv("DB_PORT"),
        db_name=os.getenv("DB_NAME"),
    )
)


if not database_exists(sync_engin.url):
    create_database(sync_engin.url)
    Base.metadata.create_all(bind=sync_engin)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
