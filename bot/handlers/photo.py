import requests
import aiohttp
from aiogram import Router, types, F
from config import DJANGO_SERVER
from keyboards import main_keyboard
from utils import is_user_allowed

router = Router()


@router.message(F.text == "📸 Сделать фото")
async def take_photo(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.")
        return

    try:
        response = requests.post(f"{DJANGO_SERVER}/camera/photo/")
        data = response.json()

        if data.get("status") == "success" and "photo_url" in data:
            photo_url = data["photo_url"]

            async with aiohttp.ClientSession() as session:
                async with session.get(photo_url) as resp:
                    if resp.status == 200:
                        photo_bytes = await resp.read()
                        await message.answer_photo(photo=photo_bytes, caption="📸 Ваше фото")
                    else:
                        await message.answer("Не удалось загрузить фото.")
        else:
            await message.answer(f"Ошибка: {data.get('message', 'Неизвестная ошибка')}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)