import time
import os

import jwt

from dotenv import load_dotenv

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
            'expires': int(time.time() + 600)
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM)
    return await token_response(token, int(time.time() + 600))


async def decodeJWT(token: str) -> str | None:
    decode_token = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
    return decode_token if decode_token['expires'] >= time.time() else None


async def get_login_by_token(token: str) -> str | None:
    decode_token = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
    return decode_token.get('user_info')