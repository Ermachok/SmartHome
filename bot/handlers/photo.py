import requests
import aiohttp
from aiogram import Router, types, F
from aiogram.types import URLInputFile
from config import DJANGO_SERVER
from keyboards import main_keyboard
import logging
from utils import is_user_allowed

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "📸 Сделать фото")
async def take_photo(message: types.Message):
    logger.info(f"Получен запрос от пользователя: {message.from_user.id}")

    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.")
        logger.warning(f"Пользователь {message.from_user.id} не имеет доступа.")
        return

    try:
        logger.info("Отправка запроса на создание фото на сервер Django...")
        response = requests.post(f"{DJANGO_SERVER}/camera/photo/")
        logger.debug(f"Ответ от Django-сервера: {response.status_code} {response.text}")

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Полученные данные: {data}")

            if data.get("status") == "success" and "photo_url" in data:
                photo_url = data["photo_url"]
                logger.info(f"Получен URL фото: {photo_url}")

                photo = URLInputFile(photo_url)
                await message.answer_photo(photo=photo, caption="📸 Ваше фото")
            else:
                error_message = data.get('message', 'Неизвестная ошибка')
                logger.error(f"Ошибка на сервере Django: {error_message}")
                await message.answer(f"Ошибка: {error_message}")
        else:
            logger.error(f"Ошибка в ответе от Django: {response.status_code}")
            await message.answer("Не удалось получить данные от сервера Django.")
    except Exception as e:
        logger.exception(f"Ошибка при обработке запроса: {e}")
        await message.answer(f"Ошибка: {e}", reply_markup=main_keyboard)
