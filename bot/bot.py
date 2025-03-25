import logging
import requests
import asyncio
import json
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
ALLOWED_USERS = config["ALLOWED_USERS"]
DJANGO_SERVER = config["DJANGO_SERVER"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Включить/выключить свет")],
        [KeyboardButton(text="📸 Сделать фото")]
    ],
    resize_keyboard=True
)


def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


@router.message(Command("start"))
async def start_command(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer(f"Извините, у вас нет доступа к этому боту.{message.from_user.id}")
        return
    await message.answer("Привет! Я управляю домом. Выбери действие:", reply_markup=keyboard)


@router.message(lambda message: message.text == "💡 Включить/выключить свет")
async def toggle_light(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("Извините, у вас нет доступа к этому боту.")
        return
    try:
        response = requests.post(f"{DJANGO_SERVER}/light/toggle/")
        status = response.json().get("status", "Ошибка")
        await message.answer(f"Свет: {status}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(lambda message: message.text == "📸 Сделать фото")
async def take_photo(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("Извините, у вас нет доступа к этому боту.")
        return
    try:
        response = requests.post(f"{DJANGO_SERVER}/camera/photo/")
        status = response.json().get("status", "Ошибка")
        await message.answer(f"Камера: {status}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
