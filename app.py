import traceback

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.bg_request_router import bg_request_router
from routes.users_router import users_router
from routes.admin_router import admin_router
from utils.bot import send_telegram_error

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        await send_telegram_error(traceback.format_exc())
        return Response("Internal server error", status_code=500)


# app.middleware('http')(catch_exceptions_middleware)

app.include_router(users_router, prefix="/api")
app.include_router(bg_request_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
