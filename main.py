import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
MODEL = os.getenv("MODEL","nex-agi/nex-n2.5-mini:free")

system_prompt = (
    "Ты — опытный IT-гик. Отвечай кратко, по делу, без воды. "
    "Если не уверен — скажи прямо."
)

print("KEY:", repr(OPENROUTER_KEY))
client = AsyncOpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key = OPENROUTER_KEY,
)

dp = Dispatcher()


async def ask_llm(user_text: str) -> str:
    try:
        response = await client.chat.completions.create(
            model = MODEL,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.exception("LMM error")
        return f"Error LLM: {e}"


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет. Напиши вопрос - отвечу.")


@dp.message()
async def handle_message(message: types.Message):
    try:
        answer = await ask_llm(message.text or "")
        await message.answer(answer)
    except Exception as e:
        logging.exception("LLM error")
        await message.answer("Произошла ошибка, попробуйте позже.")


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
