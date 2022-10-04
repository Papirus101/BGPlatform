import pytest

from utils.bot import send_sync_telegram_message


class MyPlugin:
    def pytest_sessionfinish(self, session, exitstatus):
        text_message = (
            f"🛠 <strong>Отчёт по тестикам</strong\n"
            f"Было запущено {len(session.items)} тестов\n"
            f'{"🔥 Ошибок нет" if exitstatus == 0 else "❗️ Беги чекать тесты"}'
        )
        send_sync_telegram_message(text_message)


pytest.main(["-s", "tests.py"], plugins=[MyPlugin()])
