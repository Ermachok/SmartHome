import requests
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import DJANGO_SERVER
from keyboards import main_keyboard, schedule_keyboard
from utils import is_user_allowed

WEEK_DAYS = {
    "mon": "Понедельник",
    "tue": "Вторник",
    "wed": "Среда",
    "thu": "Четверг",
    "fri": "Пятница",
    "sat": "Суббота",
    "sun": "Воскресенье",
}


class ScheduleCreation(StatesGroup):
    choosing_days = State()
    choosing_time = State()


router = Router()


@router.message(lambda message: message.text == "Настройки расписания")
async def show_schedule(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.")
        return
    await message.answer("Настройки расписания", reply_markup=schedule_keyboard)


@router.message(lambda message: message.text == "Показать все расписания")
async def show_schedules_list(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.")
        return

    response = requests.get(f"{DJANGO_SERVER}/light/schedule/")
    if response.status_code != 200:
        await message.answer("Ошибка получения расписаний.")
        return

    schedules = response.json()
    if not schedules:
        await message.answer("Нет доступных расписаний.")
        return

    for schedule in schedules:
        schedule_id = schedule.get("id")
        text = f"Расписание {schedule_id}\n🕒 {schedule.get('time')}\n📆 {', '.join(schedule.get('days', []))}\n🔘 {'✅ Активно' if schedule.get('is_active') else '❌ Неактивно'}"
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text="🗑 Удалить", callback_data=f"delete_schedule_{schedule_id}"
        )
        await message.answer(text, reply_markup=keyboard.as_markup())


@router.callback_query(lambda c: c.data.startswith("delete_schedule_"))
async def delete_schedule(callback: types.CallbackQuery):
    schedule_id = callback.data.split("_")[-1]
    response = requests.delete(
        f"{DJANGO_SERVER}/light/schedule/", json={"id": schedule_id}
    )
    status_msg = {204: "✅ Расписание удалено.", 404: "❌ Расписание не найдено."}.get(
        response.status_code, "⚠ Ошибка удаления."
    )
    await callback.message.edit_text(status_msg)
    await callback.answer()


@router.message(F.text == "⬅ Назад")
async def back_from_schedule(message: types.Message):
    """Возвращает пользователя в главное меню из раздела расписания."""
    await message.answer("Главное меню:", reply_markup=main_keyboard)


@router.message(F.text == "Установить новое расписание")
async def start_schedule_creation(message: types.Message, state: FSMContext):
    if not is_user_allowed(message.from_user.id):
        await message.answer("У вас нет доступа.")
        return

    await state.set_state(ScheduleCreation.choosing_days)
    await state.update_data(selected_days=[])
    await show_day_selection(message, state)


async def show_day_selection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get("selected_days", [])

    keyboard = InlineKeyboardBuilder()

    day_groups = [
        list(WEEK_DAYS.items())[i : i + 3] for i in range(0, len(WEEK_DAYS), 3)
    ]

    for group in day_groups:
        row = []
        for key, value in group:
            emoji = "✅" if key in selected_days else "❌"
            row.append(
                InlineKeyboardButton(
                    text=f"{emoji} {value}", callback_data=f"toggle_day_{key}"
                )
            )
        keyboard.row(*row)

    keyboard.button(text="➡ Далее", callback_data="next_to_time")
    await message.answer("Выберите дни недели:", reply_markup=keyboard.as_markup())


@router.callback_query(F.data.startswith("toggle_day_"))
async def toggle_day(callback: types.CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[-1]
    data = await state.get_data()
    selected_days = data.get("selected_days", [])

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

    await state.update_data(selected_days=selected_days)
    await callback.message.edit_reply_markup(reply_markup=None)
    await show_day_selection(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "next_to_time")
async def ask_for_time(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ScheduleCreation.choosing_time)
    await callback.message.answer("Введите время в формате HH:MM (например, 14:30):")
    await callback.answer()


@router.message(ScheduleCreation.choosing_time, F.text)
async def save_schedule(message: types.Message, state: FSMContext):
    try:
        time_str = message.text.strip()
        hours, minutes = map(int, time_str.split(":"))
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError("Некорректное время")

        data = await state.get_data()
        selected_days = data.get("selected_days", [])

        if not selected_days:
            await message.answer("Вы не выбрали ни одного дня.")
            await state.clear()
            return

        payload = {
            "time": f"{hours:02}:{minutes:02}",
            "days": selected_days,
            "is_active": True,
        }

        response = requests.post(f"{DJANGO_SERVER}/light/schedule/", json=payload)

        if response.status_code == 201:
            await message.answer("✅ Расписание успешно создано!")
        else:
            await message.answer("⚠ Ошибка создания расписания.")

    except Exception:
        await message.answer("Ошибка! Введите корректное время в формате HH:MM.")

    await state.clear()
