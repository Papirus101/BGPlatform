from sqlalchemy.orm import selectinload
from db.models.banks import Banks

from sqlalchemy import select

async def get_all_banks(session):
    sql = select(Banks).options(
            selectinload(Banks.fz_types),
            selectinload(Banks.bg_types),
            selectinload(Banks.company_type),
            selectinload(Banks.valute_types))
    data = await session.execute(sql)
    data = data.all()
        
