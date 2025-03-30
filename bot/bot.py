import logging
import requests
import asyncio
import json
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ALLOWED_USERS = config["ALLOWED_USERS"]
DJANGO_SERVER = config["DJANGO_SERVER"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Включить/выключить свет")],
        [KeyboardButton(text="🔆 Установить яркость"), KeyboardButton(text="🎨 Изменить цвет")],
        [KeyboardButton(text="📸 Сделать фото")],
    ],
    resize_keyboard=True,
)


class LightControl(StatesGroup):
    waiting_for_brightness = State()
    waiting_for_color = State()


def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


@router.message(Command("start"))
async def start_command(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer(f"У вас нет доступа к этому боту. ID: {message.from_user.id}")
        return
    await message.answer("Привет! Я управляю домом. Выбери действие:", reply_markup=keyboard)


@router.message(F.text == "💡 Включить/выключить свет")
async def toggle_light(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа к этому боту.")
        return
    try:
        response = requests.post(f"{DJANGO_SERVER}/light/toggle/")
        status = response.json().get("status", "Ошибка")
        await message.answer(f"Свет: {status}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(F.text == "🔆 Установить яркость")
async def ask_brightness(message: types.Message, state: FSMContext):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа к этому боту.")
        return
    await state.set_state(LightControl.waiting_for_brightness)
    await message.answer("Введите уровень яркости (0-100):", reply_markup=ReplyKeyboardRemove())


@router.message(LightControl.waiting_for_brightness, lambda message: message.text.isdigit() and 0 <= int(message.text) <= 100)
async def set_brightness(message: types.Message, state: FSMContext):
    brightness = int(message.text)
    try:
        response = requests.post(f"{DJANGO_SERVER}/light/brightness/", json={"brightness": brightness})
        status = response.json().get("status", "Ошибка")
        await message.answer(f"Яркость установлена на {brightness}%", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=keyboard)
    await state.clear()


@router.message(F.text == "🎨 Изменить цвет")
async def ask_color(message: types.Message, state: FSMContext):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа к этому боту.")
        return
    await state.set_state(LightControl.waiting_for_color)
    await message.answer("Введите цвет в формате R G B (например, 255 100 50):", reply_markup=ReplyKeyboardRemove())


@router.message(LightControl.waiting_for_color, lambda message: all(x.isdigit() and 0 <= int(x) <= 255 for x in message.text.split()))
async def set_color(message: types.Message, state: FSMContext):
    r, g, b = map(int, message.text.split())
    try:
        response = requests.post(f"{DJANGO_SERVER}/light/color/", json={"r": r, "g": g, "b": b})
        status = response.json().get("status", "Ошибка")
        await message.answer(f"Цвет установлен на ({r}, {g}, {b})", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=keyboard)
    await state.clear()


@router.message(F.text == "📸 Сделать фото")
async def take_photo(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа к этому боту.")
        return
    try:
        response = requests.post(f"{DJANGO_SERVER}/photo/")
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
