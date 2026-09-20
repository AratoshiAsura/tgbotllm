# Telegram LLM Bot

Telegram-бот с интеграцией LLM через OpenRouter API.

## Стек
- Python 3.14
- aiogram 3.x
- OpenAI SDK (OpenAI-совместимый API OpenRouter)
- python-dotenv
- pytest

## Что умеет
- Принимает сообщения в Telegram и отвечает через LLM.
- Системный промпт задаёт стиль ответов.
- Обрабатывает ошибки API — бот не падает.
- Покрыт тестами (мок OpenRouter).

## Запуск
1. Клонировать репозиторий.
2. Создать `.env` по образцу `.env.example`.
3. `python -m venv .venv && source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python main.py`

## Переменные окружения
- `BOT_TOKEN` — токен от @BotFather
- `OPENROUTER_KEY` — ключ от openrouter.ai
- `MODEL` — ID модели (например, `nex-agi/nex-n2.5-mini:free`)
