from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.banks import FZTypes
from db.models.bg_request import BGTypes, CompanyTypes
from db.queries.banks_q import add_new_bank_q, get_all_banks

from depends.auth.jwt_bearer import OAuth2PasswordBearerCookie

from db.session import get_session
from depends.permission import AdminPermission
from models.banks import NewBank


admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get(
    "/banks_list",
    dependencies=[Depends(OAuth2PasswordBearerCookie()), Depends(AdminPermission())],
)
async def get_banks_list(session: AsyncSession = Depends(get_session)):
    banks = await get_all_banks(session)
    return banks


@admin_router.post(
    "/add_bank",
    dependencies=[Depends(OAuth2PasswordBearerCookie()), Depends(AdminPermission())],
)
async def add_new_bank(
    session: AsyncSession = Depends(get_session), bank_info: NewBank = Body()
):
    bank_data = bank_info.__dict__
    fz_types = []
    for fz in bank_data["fz_types"]:
        fz_types.append(await session.get(FZTypes, fz))
    bg_types = []
    for bg in bank_data["bg_types"]:
        bg_types.append(await session.get(BGTypes, bg))
    company_type = []
    for cmpt in bank_data["company_type"]:
        company_type.append(await session.get(CompanyTypes, cmpt))
    bank_data["fz_types"] = fz_types
    bank_data["bg_types"] = bg_types
    bank_data["company_type"] = company_type
    await add_new_bank_q(session, **bank_data)
