from fastapi import FastAPI

from db.base import Base
from db.session import engine

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get('/')
async def main_page():
    return {'hello': 'world'}