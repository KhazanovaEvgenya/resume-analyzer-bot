import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import TELEGRAM_BOT_TOKEN
from pdf_utils import extract_text_from_pdf
from vacancy_utils import get_vacancy_text
from llm import analyze_resume


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

user_data = {}

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@dp.message(CommandStart())
async def start(message: Message):
    user_data[message.from_user.id] = {
        "resume_text": None,
        "vacancy_text": None
    }

    await message.answer(
        "Привет! Я помогу оценить резюме под конкретную вакансию.\n\n"
        "1. Сначала отправь PDF-файл с резюме.\n"
        "2. Потом отправь ссылку на вакансию hh.ru или просто текст вакансии.\n"
        "3. Я оценю резюме и дам советы по улучшению."
    )


@dp.message(F.document)
async def handle_pdf(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {
            "resume_text": None,
            "vacancy_text": None
        }

    document = message.document

    if not document.file_name.lower().endswith(".pdf"):
        await message.answer("Пожалуйста, отправь резюме именно в PDF-формате.")
        return

    await message.answer("Получила PDF. Извлекаю текст из резюме...")

    file = await bot.get_file(document.file_id)
    file_path = file.file_path

    local_path = os.path.join(DOWNLOAD_DIR, f"{user_id}_{document.file_name}")

    await bot.download_file(file_path, local_path)

    try:
        resume_text = extract_text_from_pdf(local_path)
        user_data[user_id]["resume_text"] = resume_text

        await message.answer(
            "Резюме успешно прочитано.\n\n"
            "Теперь отправь ссылку на вакансию hh.ru или текст вакансии."
        )

    except Exception as e:
        await message.answer(
            f"Не удалось прочитать PDF.\n\n"
            f"Ошибка: {e}\n\n"
            "Попробуй отправить другой PDF или файл, где текст можно выделить мышкой."
        )


@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {
            "resume_text": None,
            "vacancy_text": None
        }

    if not user_data[user_id]["resume_text"]:
        await message.answer(
            "Сначала отправь PDF-файл с резюме, а потом вакансию."
        )
        return

    await message.answer("Получила вакансию. Анализирую резюме под неё...")

    vacancy_text = get_vacancy_text(message.text)
    user_data[user_id]["vacancy_text"] = vacancy_text

    try:
        result = analyze_resume(
            resume_text=user_data[user_id]["resume_text"],
            vacancy_text=vacancy_text
        )

        max_length = 3900

        if len(result) <= max_length:
            try:
                await message.answer(result, parse_mode=ParseMode.MARKDOWN)
            except:
                # если Markdown сломался — отправляем как обычный текст
                await message.answer(result)
        else:
            parts = [
                result[i:i + max_length]
                for i in range(0, len(result), max_length)
            ]

            for part in parts:
                try:
                    await message.answer(part, parse_mode=ParseMode.MARKDOWN)
                except:
                    await message.answer(part)

    except Exception as e:
        await message.answer(
            f"Во время анализа произошла ошибка:\n\n{e}"
        )


async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())