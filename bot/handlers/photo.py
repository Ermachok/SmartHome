import requests
from aiogram import Router, types
from config import DJANGO_SERVER
from keyboards import main_keyboard
from utils import is_user_allowed

router = Router()


@router.message(lambda message: message.text == "📸 Сделать фото")
async def take_photo(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.")
        return
    try:
        response = requests.post(f"{DJANGO_SERVER}/photo/")
        await message.answer(
            f"Камера: {response.json().get('status', 'Ошибка')}",
            reply_markup=main_keyboard,
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)
