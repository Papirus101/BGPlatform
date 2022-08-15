import aiohttp
import os
import datetime

import requests

# Функция для отправки сообщений об ошибке в чатик телеграм
async def send_telegram_error(text: str):
    token = os.getenv("BOT_TOKEN")
    url = "https://api.telegram.org/bot"
    channel_id = "@BGErrorsChanel"
    url += token
    method = url + "/sendMessage"
    message = f'🧍 <b>{os.environ.get("USERNAME")}</b>' \
              f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")} ⏱\n' \
              f'<code>{text}</code>'
    session = aiohttp.ClientSession()
    await session.post(method, data={
            "chat_id": channel_id,
            "text": message,
            'parse_mode': 'HTML'
        })
    await session.close()

def send_sync_telegram_message(text: str):
    token = os.getenv("BOT_TOKEN")
    url = "https://api.telegram.org/bot"
    channel_id = "@BGErrorsChanel"
    url += token
    method = url + "/sendMessage"
    message = f'🧍 <b>{os.environ.get("USERNAME")}</b>' \
              f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")} ⏱\n' \
              f'<code>{text}</code>'
    requests.post(method, json={
            "chat_id": channel_id,
            "text": message,
            'parse_mode': 'HTML'
        })
