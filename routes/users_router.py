from fastapi import (
    APIRouter,
    Response,
    HTTPException,
    Body,
    Depends,
    Request,
    UploadFile,
)

from depends.auth.jwt_bearer import OAuth2PasswordBearerCookie
from depends.auth.password_hash import hash_password, validate_password
from depends.auth.jwt_handler import signJWT, get_login_by_token
from db.session import get_session

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import (
    LoginResponseSchema,
    UserRegisterSchema,
    UserLoginSchema,
    UserAllInfoSchema,
    UserUpdateSchema,
    UserDeleteSchema,
)
from db.queries.users_q import (
    check_user_created,
    create_new_user,
    get_user_by_login,
    update_user_info_q,
)

from parser.parser_zakupki import ZachetniyBiznesParser

from utils.utils import get_user_token

import settings
import aiofiles

users_router = APIRouter(prefix="/user", tags=["users"])


@users_router.post(
    "/signup", status_code=201, responses={400: {"error": "inn invalid"}}
)
async def user_signup(
    response: Response,
    user: UserRegisterSchema = Body(),
    session: AsyncSession = Depends(get_session),
):
    await check_user_created(session, user.login)
    if user.user_type == "admin":
        raise HTTPException(400)
    user.password = await hash_password(user.password)
    session_parser = ZachetniyBiznesParser()
    user.name_organization = await session_parser.get_company_name(user.inn)
    if user.name_organization is None:
        raise HTTPException(400, "Invalid data")
    await session_parser.close_session()
    new_user = await create_new_user(session, **dict(user))
    if new_user is not None and "error" in new_user:
        raise HTTPException(400, new_user)
    token = await signJWT(user.login)
    if settings.DEBUG:
        response.headers["Authorization"] = f"Bearer {token['access_token']}"
    else:
        response.set_cookie(
            "Authorization", f"Bearer {token['access_token']}", expires=token["expires"]
        )
    return {"Authorization": f"Bearer {token['access_token']}"}


@users_router.post("/login", response_model=LoginResponseSchema)
async def user_login(
    response: Response,
    user: UserLoginSchema = Body(),
    session: AsyncSession = Depends(get_session),
):
    loggined_user = await get_user_by_login(session, user.login)
    if loggined_user is None:
        raise HTTPException(400, {"error": "user not found"})
    if not await validate_password(user.password, loggined_user.password):
        raise HTTPException(401, {"error": "password invalid"})
    token = await signJWT(user.login)
    if settings.DEBUG:
        response.headers["Authorization"] = f"Bearer {token['access_token']}"
    else:
        response.set_cookie(
            "Authorization",
            f"Bearer {token['access_token']}",
            expires=token["expires"],
            httponly=True,
            samesite="Lax",
            secure=False,
        )
    return {
        "user_info": loggined_user.__dict__,
        "Authorization": f"Bearer {token['access_token']}",
    }


@users_router.get(
    "/me",
    dependencies=[Depends(OAuth2PasswordBearerCookie())],
    response_model=UserAllInfoSchema,
)
async def get_user_info(request: Request, session: AsyncSession = Depends(get_session)):
    token = await get_user_token(request)
    user_login = await get_login_by_token(token)
    user_info = await get_user_by_login(session, user_login)
    return user_info.__dict__


@users_router.put(
    "/me",
    dependencies=[Depends(OAuth2PasswordBearerCookie())],
    response_model=UserAllInfoSchema,
)
async def update_user_info(
    request: Request,
    user_request: UserUpdateSchema = Body(),
    session: AsyncSession = Depends(get_session),
):
    token = await get_user_token(request)
    user_login = await get_login_by_token(token)
    user: dict = {k: v for k, v in user_request.__dict__.items() if v is not None}
    if "password" in user:
        user["password"] = await hash_password(user["password"])
    if "inn" in user:
        session_parser = ZachetniyBiznesParser()
        user["name_organization"] = await session_parser.get_company_name(user["inn"])
        if user["name_organization"] is None:
            raise HTTPException(400, "Invalid inn")
        await session_parser.close_session()
    await update_user_info_q(session, user_login, **user)
    new_user_info = await get_user_by_login(session, user_login)
    return new_user_info.__dict__


@users_router.post(
    "/update_photo",
    dependencies=[Depends(OAuth2PasswordBearerCookie())],
    status_code=204,
)
async def update_user_photo(
    request: Request, photo: UploadFile, session: AsyncSession = Depends(get_session)
):
    if photo.content_type.find("image") == -1:
        raise HTTPException(404, "not valid photo")
    token = await get_user_token(request)
    user_login = await get_login_by_token(token)
    user_info = await get_user_by_login(session, user_login)
    file_path = settings.USER_PHOTO_PATH.format(
        filename=f"{user_info.email}.jpg", user_type=user_info.user_type.code
    )
    async with aiofiles.open(file_path, "wb") as out_file:
        photo_content = await photo.read()
        await out_file.write(photo_content)
    await update_user_info_q(session, user_login, photo=file_path)
    return Response("", 204)


@users_router.get("/logout", dependencies=[Depends(OAuth2PasswordBearerCookie())])
async def logout(response: Response):
    response.delete_cookie("Authorization")
    return True


@users_router.post("/delete_user", dependencies=[Depends(OAuth2PasswordBearerCookie())])
async def delete_user(
    response: Response,
    request: Request,
    info: UserDeleteSchema = Body(),
    session: AsyncSession = Depends(get_session),
):
    token = await get_user_token(request)
    user_login = await get_login_by_token(token)
    info_deleted: dict = {k: v for k, v in info.__dict__.items() if v is not None}
    info_deleted["deleted"] = True
    await update_user_info_q(session, user_login, **info_deleted)
    response.delete_cookie("Authorization")
