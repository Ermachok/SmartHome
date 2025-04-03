import requests
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from config import DJANGO_SERVER
from keyboards import COLORS, color_keyboard, main_keyboard
from utils import is_user_allowed

router = Router()


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
        status = response.json()

        if status.get("status", "error") == "error":
            raise Exception

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
        requests.post(f"{DJANGO_SERVER}/light/color/", json={"r": r, "g": g, "b": b})
        await message.answer(
            f"Цвет установлен: {message.text} ({r}, {g}, {b})",
            reply_markup=main_keyboard,
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)
