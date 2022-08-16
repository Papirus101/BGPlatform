import asyncio
import os

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
from db.queries.bg_request_q import bg_request_banks_insert, update_request_info
from db.session import get_session
from parser.parser_zakupki import ZakupkiParse, ZachetniyBiznesParser
from rabbit_send.publisher import send_message
from dotenv import load_dotenv

async def on_message_zachet(message: AbstractIncomingMessage) -> None:
    session = ZachetniyBiznesParser()
    db_session = await anext(get_session())
    print(db_session)
    print("Start parse zachet")
    inn, request_id = message.body.decode().split('_')
    await session.get_info_company_request(inn, int(request_id), db_session)


async def on_message_zakupki(message: AbstractIncomingMessage) -> None:
    session = ZakupkiParse()
    db_session = await anext(get_session())
    print('Start parse zakupki')
    purchase_id, request_id = message.body.decode().split('_')
    info = await session.test(purchase_id, int(request_id), db_session)
    if info is None:
        return
    await send_message(request_id, 'start_scoring')


async def scoring_start(message: AbstractIncomingMessage) -> None:
    print('Start', message.body.decode())
    db_session = await anext(get_session())
    await bg_request_banks_insert(db_session, int(message.body.decode()))
    await update_request_info(db_session, int(message.body.decode()), is_ready=True)

async def main() -> None:
    load_dotenv('.env')
    connection = await connect(host=os.getenv('RABBIT_HOST'))
    async with connection:
        channel = await connection.channel()
        queue_zachet = await channel.declare_queue("parse_zachet")
        await queue_zachet.consume(on_message_zachet, no_ack=True)
        queue_zalupki = await channel.declare_queue("parse_zakupki")
        await queue_zalupki.consume(on_message_zakupki, no_ack=True)
        queue_scoring = await channel.declare_queue('start_scoring')
        await queue_scoring.consume(scoring_start, no_ack=True)
        print(" [*] Waiting for messages. To exit press CTRL+C")
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
