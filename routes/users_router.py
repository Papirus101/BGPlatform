from fastapi import APIRouter, Response, HTTPException, Body, Depends, Request

from depends.auth.jwt_bearer import OAuth2PasswordBearerCookie
from depends.auth.password_hash import hash_password, validate_password
from depends.auth.jwt_handler import signJWT, get_login_by_token

from models.user import LoginResponseSchema, UserRegisterSchema, UserLoginSchema, UserInfoSchema, UserAllInfoSchema, UserUpdateSchema, \
    UserDeleteSchema
from db.queries.users_q import create_new_user, get_user_by_login, update_user_info_q
from db.session import async_sessionmaker

from parser.parser_zakupki import ZachetniyBiznesParser
import settings
from utils.utils import get_user_token

users_router = APIRouter(
    prefix='/user',
    tags=['users']
)


@users_router.post('/signup', status_code=201, responses={400: {'error': 'inn invalid'}})
async def user_signup(response: Response, user: UserRegisterSchema = Body()):
    user.password = await hash_password(user.password)
    session = ZachetniyBiznesParser()
    user.name_organization = await session.get_company_name(user.inn)
    if user.name_organization is None:
        raise HTTPException(400, 'Invalid data')
    await session.close_session()
    new_user = await create_new_user(async_sessionmaker, **dict(user))
    if new_user is not None and 'error' in new_user:
        raise HTTPException(400, new_user)
    token = await signJWT(user.login)
    if settings.DEBUG:
        response.headers['Authorization'] = f"Bearer {token['access_token']}"
    else:
        response.set_cookie('Authorization', f"Bearer {token['access_token']}",
                        expires=token['expires'],
                        httponly=True,
                        samesite='Lax',
                        secure=False)
    return {'Authorization': f"Bearer {token['access_token']}"}


@users_router.post('/login', response_model=LoginResponseSchema)
async def user_login(response: Response, user: UserLoginSchema = Body()):
    loggined_user = await get_user_by_login(async_sessionmaker, user.login)
    if loggined_user is None:
        raise HTTPException(400, {'error': 'user not found'})
    if not await validate_password(user.password, loggined_user.password):
        raise HTTPException(401, {'error': 'password invalid'})
    token = await signJWT(user.login)
    if settings.DEBUG:
        response.headers['Authorization'] = f"Bearer {token['access_token']}"
    else:
        response.set_cookie('Authorization', f"Bearer {token['access_token']}",
                        expires=token['expires'],
                        httponly=True,
                        samesite='Lax',
                        secure=False)
    return {'user_info': loggined_user.__dict__,
            'Authorization': f"Bearer {token['access_token']}"}


@users_router.get('/me', dependencies=[Depends(OAuth2PasswordBearerCookie())], response_model=UserAllInfoSchema)
async def get_user_info(request: Request):
    token = await get_user_token(request)
    user_login = await get_login_by_token(token)
    user_info = await get_user_by_login(async_sessionmaker, user_login)
    return user_info.__dict__


@users_router.put('/me', dependencies=[Depends(OAuth2PasswordBearerCookie())], response_model=UserAllInfoSchema)
async def update_user_info(request: Request, user: UserUpdateSchema = Body()):
    if user.user_id is None:
        token = await get_user_token(request)
        user_login = await get_login_by_token(token)
        user: dict = {k:v for k, v in user.__dict__.items() if v is not None}
        if 'password' in user:
            user['password'] = await hash_password(user['password'])
        if 'inn' in user:
            session = ZachetniyBiznesParser()
            user['name_organization'] = await session.get_company_name(user['inn'])
            if user['name_organization'] is None:
                raise HTTPException(400, 'Invalid inn')
            await session.close_session()
        await update_user_info_q(async_sessionmaker, user_login, **user)
        new_user_info = await get_user_by_login(async_sessionmaker, user_login)
        return new_user_info.__dict__


@users_router.get('/logout', dependencies=[Depends(OAuth2PasswordBearerCookie())])
async def logout(response: Response):
    response.delete_cookie('Authorization')
    return True


@users_router.post('/delete_user', dependencies=[Depends(OAuth2PasswordBearerCookie())])
async def delete_user(response: Response, request: Request, info: UserDeleteSchema = Body()):
    token = await get_user_token(request)
    user_login = await get_login_by_token(token)
    info_deleted = dict(info)
    new_info = {'deleted': True}
    for elem in info_deleted.keys():
        if info_deleted[elem] is not None:
            new_info[elem] = info_deleted[elem]
    await update_user_info_q(async_sessionmaker, user_login, **new_info)
    response.delete_cookie('Authorization')
