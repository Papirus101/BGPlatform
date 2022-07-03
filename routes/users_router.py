from fastapi import APIRouter, Response, HTTPException, Body, Depends, Request

from depends.auth.jwt_bearer import OAuth2PasswordBearerCookie
from depends.auth.password_hash import hash_password, validate_password
from depends.auth.jwt_handler import signJWT, get_login_by_token

from models.user import UserRegisterSchema, UserLoginSchema, UserInfoSchema, UserAllInfoSchema
from db.queries.users_q import create_new_user, get_user_by_login
from db.session import async_sessionmaker

users_router = APIRouter(
    prefix='/user',
    tags=['users']
)


@users_router.post('/signup', status_code=201)
async def user_signup(response: Response, user: UserRegisterSchema = Body()):
    user.password = await hash_password(user.password)
    new_user = await create_new_user(async_sessionmaker, **dict(user))
    if new_user is not None and 'error' in new_user:
        raise HTTPException(400, new_user)
    token = await signJWT(user.login)
    response.set_cookie('Bearer', token['access_token'], expires=token['expires'])
    return True


@users_router.post('/login', response_model=UserInfoSchema)
async def user_login(response: Response, user: UserLoginSchema = Body()):
    loggined_user = await get_user_by_login(async_sessionmaker, user.login)
    if loggined_user is None:
        raise HTTPException(400, {'error': 'user not found'})
    if not await validate_password(user.password, loggined_user.password):
        raise HTTPException(401, {'error': 'password invalid'})
    token = await signJWT(user.login)
    response.set_cookie('Authorization', f"Bearer {token['access_token']}", expires=token['expires'])
    return loggined_user.__dict__


@users_router.get('/me', dependencies=[Depends(OAuth2PasswordBearerCookie())], response_model=UserAllInfoSchema)
async def get_user_info(request: Request):
    _, token = request.cookies.get('Authorization').split()
    user_login = await get_login_by_token(token)
    user_info = await get_user_by_login(async_sessionmaker, user_login)
    return user_info.__dict__
