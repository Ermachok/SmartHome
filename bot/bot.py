import asyncio
import json
import logging
from http.client import responses

import requests
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ALLOWED_USERS = config["ALLOWED_USERS"]
DJANGO_SERVER = config["DJANGO_SERVER"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

COLORS = {
    "🔴 Кровавая Мэри": (255, 0, 0),
    "🟠 Апельсиновый щербет": (255, 165, 0),
    "🟡 Лимонный щербет": (255, 255, 0),
    "🟢 Лесная зелень": (0, 255, 0),
    "🟦 Морской бриз": (0, 191, 255),
    "🔵 Глубокий океан": (0, 0, 255),
    "🟣 Магический фиолет": (128, 0, 128),
    "🌿 Изумрудная долина": (80, 200, 120),
    "💖 Розовый закат": (255, 105, 180),
    "⚪ Снежная вуаль": (255, 255, 255),
    "🧈 Сливочное масло": (255, 239, 100),
}

color_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=color)] for color in COLORS.keys()]
    + [[KeyboardButton(text="⬅ Назад")]],
    resize_keyboard=True,
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Включить/выключить свет")],
        [
            KeyboardButton(text="🔆 Установить яркость"),
            KeyboardButton(text="🎨 Изменить цвет лампы"),
        ],
        [KeyboardButton(text="📸 Сделать фото")],
    ],
    resize_keyboard=True,
)


def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


@router.message(Command("start"))
async def start_command(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer(f"У вас нет доступа. ID: {message.from_user.id}")
        return
    await message.answer("Привет! Выбери действие:", reply_markup=main_keyboard)


@router.message(F.text == "💡 Включить/выключить свет")
async def toggle_light(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.", reply_markup=main_keyboard)
        return

    try:
        response = requests.post(f"{DJANGO_SERVER}/light/toggle/")
        light_status = response.json().get("status")
        await message.answer(f"Свет {light_status}", reply_markup=main_keyboard)
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)


@router.message(F.text == "🔆 Установить яркость")
async def ask_brightness(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.", reply_markup=main_keyboard)
        return
    await message.answer("Введите уровень яркости (0-100):", reply_markup=main_keyboard)


@router.message(
    lambda message: message.text.isdigit() and 0 <= int(message.text) <= 100
)
async def set_brightness(message: types.Message):
    brightness = int(message.text)
    try:
        response = requests.post(
            f"{DJANGO_SERVER}/light/brightness/", json={"brightness": brightness}
        )
        status = response.json().get("status", "Ошибка")
        await message.answer(
            f"Яркость установлена на {brightness}%", reply_markup=main_keyboard
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)


@router.message(F.text == "🎨 Изменить цвет лампы")
async def show_colors(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.", reply_markup=main_keyboard)
        return
    await message.answer("Выберите цвет:", reply_markup=color_keyboard)


@router.message(lambda message: message.text in COLORS)
async def set_color(message: types.Message):
    r, g, b = COLORS[message.text]
    try:
        response = requests.post(
            f"{DJANGO_SERVER}/light/color/", json={"r": r, "g": g, "b": b}
        )
        status = response.json().get("status", "Ошибка")
        await message.answer(
            f"Цвет установлен: {message.text} ({r}, {g}, {b})",
            reply_markup=main_keyboard,
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)


@router.message(F.text == "⬅ Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_keyboard)


@router.message(F.text == "📸 Сделать фото")
async def take_photo(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.", reply_markup=main_keyboard)
        return
    try:
        response = requests.post(f"{DJANGO_SERVER}/photo/")
        status = response.json().get("status", "Ошибка")
        await message.answer(f"Камера: {status}", reply_markup=main_keyboard)
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
