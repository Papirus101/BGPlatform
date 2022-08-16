from aio_pika import Message, connect
import os
from dotenv import load_dotenv

load_dotenv('.env')

async def send_message(message: str, route: str):
    connection = await connect(host=os.getenv('RABBIT_HOST'))
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(route)
        await channel.default_exchange.publish(
            Message(message.encode()),
            routing_key=queue.name,
        )
