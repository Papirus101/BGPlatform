import time
import os
from fastapi import HTTPException

import jwt

from dotenv import load_dotenv

from db.queries.users_q import get_user_by_login
from db.session import get_session

import settings

load_dotenv('.env')

JWT_SECRET = os.getenv('SECRET')
JWT_ALGORITHM = os.getenv('ALGORITHM')


async def token_response(token: str, expires: int) -> dict:
    """
    FUNCTION FOR RETURN TOKEN FROM ROUTER
    :param expires:
    :param token:
    :return:
    """
    return {
        'access_token': token,
        'expires': expires
    }


async def signJWT(user_info: str) -> dict:
    token = jwt.encode(
        {
            'user_info': user_info,
            'expires': int(time.time() + 7200)
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM)
    return await token_response(token, int(time.time() + 7200))


async def decodeJWT(token: str) -> str | None:
    if isinstance(token, list):
        token = token[0]
    token = token.encode('utf-8')
    decode_token = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
    return decode_token if decode_token['expires'] >= time.time() else None


async def get_user_by_token(token, db_session):
    user_login = await get_login_by_token(token)
    return await get_user_by_login(db_session, user_login)


async def get_login_by_token(token: str) -> str:
    if isinstance(token, list):
        token = token[1]
    token = token.encode('utf-8')
    decode_token = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
    if decode_token.get('user_info') is None:
        raise HTTPException(403)
    return decode_token['user_info']
