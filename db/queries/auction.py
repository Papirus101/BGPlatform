# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select,or_
# from sqlalchemy.orm import selectinload
#
# from db.models.users import Auction, AuctionBrokers, User
# from db.models.bg_request import BGRequest
#
# import datetime
#
#
# async def create_auction_q(db_session: AsyncSession, request_id: int, date_finish: str, brokers: list[int],
#                            all_brokers: bool):
#     async with db_session() as session:
#         new_auction = Auction(request_id=request_id,
#                               finish=date_finish,
#                               all_brokers=all_brokers)
#         if not all_brokers:
#             brokers_list = []
#             for broker in brokers:
#                 sql = select(User).where(User.id == broker)
#                 data = await session.execute(sql)
#                 broker_data = data.one()
#                 brokers_list.append(broker_data[0])
#             new_auction.brokers = brokers_list
#         await session.merge(new_auction)
#         await session.commit()
#
#
# async def get_all_auctions_for_user_q(db_session: AsyncSession, user_id: int):
#     async with db_session() as session:
#         sql = select(Auction).options(selectinload(Auction.brokers)).where(
#             or_(Auction.all_brokers == False, Auction.brokers == user_id)
#         )
#         data = await session.execute(sql)
#         data = data.all()
#         print(data)
#         for d in data:
#             for broker in d[0].brokers:
#                 print(broker.fio)
# #
