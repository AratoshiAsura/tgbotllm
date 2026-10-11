# Cheatsheet: tgbotllm

Конспект по функциям и приёмам, использованным в Telegram-боте с LLM.

## 1. aiogram

### `Bot(token=...)`
**Что:** объект бота, через него идут все запросы к Telegram API.

```python
from aiogram import Bot

bot = Bot(token=os.getenv("BOT_TOKEN"))
```

### `Dispatcher()`
**Что:** маршрутизатор сообщений. Сюда регистрируются все хендлеры.

```python
from aiogram import Dispatcher

dp = Dispatcher()
```

### `@dp.message(Command("start"))`
**Что:** хендлер команды `/start`.

```python
from aiogram.filters import Command
from aiogram import types

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет. Пиши вопрос — отвечу.")
```

### `@dp.message()`
**Что:** хендлер всех остальных сообщений (без фильтра).

```python
@dp.message()
async def handle_message(message: types.Message):
    answer = await ask_llm(message.text or "")
    await message.answer(answer)
```

### `message.answer(text)`
**Что:** отправить ответ в тот же чат.

```python
await message.answer("Думаю...")
```

### `dp.start_polling(bot)`
**Что:** запускает бесконечный цикл получения сообщений от Telegram.

```python
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 2. LLM (OpenRouter)

### `AsyncOpenAI(base_url=..., api_key=...)`
**Что:** асинхронный клиент OpenAI-совместимого API.

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_KEY"),
)
```

### `ask_llm(text)`
**Что:** отправляет сообщение в LLM и возвращает ответ. При ошибке возвращает строку с описанием (бот не падает).

```python
async def ask_llm(user_text: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.exception("LLM error")
        return f"Ошибка LLM: {e}"
```

### `SYSTEM_PROMPT`
**Что:** задаёт стиль и роль модели. Одно сообщение в начале диалога.

```python
SYSTEM_PROMPT = (
    "Ты — опытный IT-гик. Отвечай кратко, по делу, без воды. "
    "Если не уверен — скажи прямо."
)
```

---

## 3. Env-переменные

```python
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
MODEL = os.getenv("MODEL", "meta-llama/llama-3.1-8b-instruct:free")
```

`.env`:
```
BOT_TOKEN=123456:ABC...
OPENROUTER_KEY=sk-or-v1-...
MODEL=nex-agi/nex-n2.5-mini:free
```

**Правило:** `.env` в `.gitignore`, `.env.example` — в репозитории (без ключей).

---

## 4. Тесты (pytest)

### `AsyncMock(return_value=...)`
**Что:** мок для async-функции `ask_llm` — чтобы тесты не ходили в реальный API.

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_ask_llm_returns_content():
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content="Привет из мока"))
    ]
    with patch("main.client.chat.completions.create", return_value=mock_response):
        result = await ask_llm("тест")
    assert result == "Привет из мока"
```

### `side_effect=Exception(...)`
**Что:** заставляет мок поднять исключение — для проверки обработки ошибок.

```python
@pytest.mark.asyncio
async def test_ask_llm_handles_error():
    with patch("main.client.chat.completions.create", side_effect=Exception("API down")):
        result = await ask_llm("тест")
    assert "Ошибка LLM" in result
```

### `pytest.ini`
```ini
[pytest]
asyncio_mode = auto
pythonpath = .
```

---

## 5. Docker

### `Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

**Важно:** у бота **нет `EXPOSE`** — он не слушает порт, а сам подключается к Telegram API через polling.

### `.dockerignore`
```
.env
.venv/
__pycache__/
.pytest_cache/
*.pyc
.git/
```

### Команды
```bash
docker build -t tgbotllm .                    # собрать
docker run --env-file .env tgbotllm           # запустить (foreground)
docker run -d --env-file .env --name tgbot tgbotllm   # в фоне
docker ps                                     # запущенные
docker logs -f <id>                           # логи в реальном времени
docker stop <id>                              # остановить
```

---

## 6. Логирование

```python
import logging

logging.basicConfig(level=logging.INFO)
```

**Зачем:** aiogram пишет в лог старт polling, ошибки сети, получение сообщений. Без `basicConfig` логи не видны.

---

## 7. Частые ошибки

### `TelegramNetworkError: Request timeout`
**Причина:** контейнер не может достучаться до `api.telegram.org`.
**Решение:** проверить сеть (`docker run --rm alpine ping -c 2 8.8.8.8`), при необходимости — `--network host` или прокси.

### `Import could not be resolved`
**Причина:** venv не активирован или интерпретатор в IDE не выбран.
**Решение:** `source .venv/bin/activate`, затем `Ctrl+Shift+P` → Python: Select Interpreter → `./.venv/bin/python`.

### `ModuleNotFoundError: No module named 'aiogram.filtres'`
**Причина:** опечатка. Модуль называется `filters`, а не `filtres`.
**Решение:** `from aiogram.filters import Command`.
