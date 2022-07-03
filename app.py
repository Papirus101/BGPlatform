from fastapi import FastAPI

from db.base import Base
from db.session import engine

from routes.users_router import users_router

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(users_router)