from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db.base import Base
from db.session import engine

from routes.bg_request_router import bg_request_router
from routes.users_router import users_router

app = FastAPI(
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        openapi_url='/api/openapi.json',
        )

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#async def catch_exceptions_middleware(request: Request, call_next):
#    try:
#        return await call_next(request)
#    except Exception:
#        return Response("Internal server error", status_code=500)
#
#app.middleware('http')(catch_exceptions_middleware)


#@app.on_event("startup")
#async def startup_event():
#    async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.create_all)


app.include_router(users_router, prefix='/api')
app.include_router(bg_request_router, prefix='/api')
