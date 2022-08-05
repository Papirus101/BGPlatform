from fastapi import APIRouter, HTTPException, Body, Depends, Request
from db.queries.banks_q import get_all_banks

from db.queries.bg_request_q import add_new_bg_request, bg_request_banks_insert, get_bg_types_q, get_fz_type_by_name, get_specifics_works_q, get_user_requests_query, get_user_request_query, test_query
from depends.auth.jwt_bearer import OAuth2PasswordBearerCookie
from depends.auth.jwt_handler import get_user_by_token
from models.bg_request_model import BGRequestCreateSchema, BGRequestDetailInfoSchema, BGRequestsListSchema, BGTypesSpicificsListShema

from db.session import async_sessionmaker
from parser.parser_zakupki import ZakupkiParse
from rabbit_send.publisher import send_message

bg_request_router = APIRouter(prefix='/bg_request',
                              tags=['bg_request'])


@bg_request_router.post('/new_bg_request', dependencies=[Depends(OAuth2PasswordBearerCookie())],
                        response_model=BGRequestCreateSchema)
async def create_new_bg_request(request: Request, bg_request: BGRequestCreateSchema = Body()):
    user = await get_user_by_token(request.cookies)
    new_bg = await add_new_bg_request(async_sessionmaker, user_id=user.id, **(dict(bg_request)))
    await send_message(f'{bg_request.inn}_{new_bg.id}', 'parse_zachet')
    await send_message(f'{bg_request.purchase_number}_{new_bg.id}', 'parse_zakupki')
    return bg_request


@bg_request_router.post('/get_user_request', dependencies=[Depends(OAuth2PasswordBearerCookie())],
                        response_model=BGRequestDetailInfoSchema,
                        responses={404: {'NOT FOUND': "NOT FOUND REQUESTS FROM USER"}})
async def get_user_request_info(request: Request, request_id: int):
    user = await get_user_by_token(request.cookies)
    data = await get_user_request_query(async_sessionmaker, user.id, request_id)
    if data is None:
        raise HTTPException(404, {'NOT FOUND': "NOT FOUND REQUESTS FROM USER"})
    return data.__dict__


@bg_request_router.get('/get_user_requests', dependencies=[Depends(OAuth2PasswordBearerCookie())],
                       response_model=BGRequestsListSchema)
async def get_user_requests(request: Request):
    user = await get_user_by_token(request.cookies)
    data = await get_user_requests_query(async_sessionmaker, user.id)
    return BGRequestsListSchema.parse_obj({'requests': data})


@bg_request_router.get('/get_work_specifics', dependencies=[Depends(OAuth2PasswordBearerCookie())],
        response_model=BGTypesSpicificsListShema)
async def get_work_specifics():
    data = await get_specifics_works_q(async_sessionmaker)
    return {'data': data}


@bg_request_router.get('/get_bg_types', dependencies=[Depends(OAuth2PasswordBearerCookie())],
        response_model=BGTypesSpicificsListShema)
async def get_bg_types():
    data = await get_bg_types_q(async_sessionmaker)
    return {'data': data}


@bg_request_router.get('/test_query')
async def test_request():
    await test_query(async_sessionmaker)
    await get_fz_type_by_name(async_sessionmaker, '44 ')
    await get_all_banks(async_sessionmaker)
    d = await bg_request_banks_insert(async_sessionmaker, 10)


@bg_request_router.get('/check_zakupki_gov', dependencies=[Depends(OAuth2PasswordBearerCookie())],
                       status_code=200, responses={503: {'service_offline': 'zskupki.gov offline'}})
async def check_zakupki_gov_available():
    session = ZakupkiParse()
    status_code = await session.check_available()
    if not status_code:
        raise HTTPException(503, {'service_offline': 'zskupki.gov offline'})


# @bg_request_router.post('/start_auction', dependencies=[Depends(OAuth2PasswordBearerCookie())])
# async def start_auction(request: Request, auction_info: BGRequestAuctionStart = Body()):
#     await create_auction_q(async_sessionmaker, **dict(auction_info))
#
#
# @bg_request_router.get('/get_auctions', dependencies=[Depends(OAuth2PasswordBearerCookie())])
# async def get_auctions(request: Request):
#     user = await get_user_by_token(request.cookies)
#     await get_all_auctions_for_user_q(async_sessionmaker, user.id)
