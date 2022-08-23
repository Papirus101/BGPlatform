from fastapi import Depends, HTTPException, Request
from dotenv import load_dotenv

from db.session import get_session
from depends.auth.jwt_handler import get_user_by_token

from utils.utils import get_user_token

load_dotenv('.env')


class AdminPermission:
    async def __call__(self, request: Request, session = Depends(get_session)):
        user = await get_user_by_token(await get_user_token(request), session)
        if user.user_type != 'admin':
            raise HTTPException(403)
